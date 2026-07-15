from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import unicodedata
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Any

from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (
    QApplication,
    QCheckBox,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSplitter,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


ROLES = [
    "Specifier",
    "Coder",
    "Cleaner",
    "Architect",
    "Hardender",
    "QA",
    "AntracytowyMaster",
]


@dataclass
class TaskItem:
    title: str
    body: str
    slice_id: str = ""
    state: str = "pending"
    sent_at: str = ""


class SwarmForgeTaskSender(QMainWindow):
    def __init__(self, project_root: Path) -> None:
        super().__init__()
        self.project_root = project_root
        self.state_file = project_root / ".swarmforge" / "gui_tasks.json"
        self.outbox_dir = project_root / ".swarmforge" / "gui_outbox"
        self.gui_dir = project_root / "agent_context" / "gui"
        self.slices_file = self.gui_dir / "slices.json"
        self.slices_ready_file = self.gui_dir / "slices_ready.md"
        self.completed_slices_dir = self.gui_dir / "completed_slices"
        self.outbox_dir.mkdir(parents=True, exist_ok=True)
        self.gui_dir.mkdir(parents=True, exist_ok=True)
        self.completed_slices_dir.mkdir(parents=True, exist_ok=True)
        self.tasks: list[TaskItem] = []
        self.role_labels: dict[str, QLabel] = {}
        self.activity_seen_after_send = False
        self.loaded_slices_mtime = 0.0
        self.last_slices_error = ""

        self.setWindowTitle(f"Swarm-Forge Task Sender - {project_root}")
        self.resize(1220, 760)
        self._build_ui()
        self._load_state()
        self._refresh_task_list()
        self._refresh_agent_status()

        self.status_timer = QTimer(self)
        self.status_timer.timeout.connect(self._tick)
        self.status_timer.start(2000)

    def _build_ui(self) -> None:
        root = QWidget()
        main_layout = QVBoxLayout(root)

        top_splitter = QSplitter(Qt.Orientation.Horizontal)
        self.description_editor = QTextEdit()
        self.description_editor.setPlaceholderText(
            "Wklej duzy opis funkcji, MVP albo rozszerzenia aplikacji."
        )
        top_splitter.addWidget(self._boxed("Opis wejściowy", self.description_editor))

        self.task_list = QListWidget()
        self.task_list.currentRowChanged.connect(self._show_selected_task)
        top_splitter.addWidget(self._boxed("Taski / slice'y", self.task_list))
        top_splitter.setSizes([760, 360])
        main_layout.addWidget(top_splitter, 5)

        preview_splitter = QSplitter(Qt.Orientation.Horizontal)
        self.task_preview = QTextEdit()
        self.task_preview.textChanged.connect(self._update_selected_task_body)
        preview_splitter.addWidget(self._boxed("Podgląd i edycja taska", self.task_preview))

        self.log_view = QTextEdit()
        self.log_view.setReadOnly(True)
        preview_splitter.addWidget(self._boxed("Log", self.log_view))
        preview_splitter.setSizes([760, 360])
        main_layout.addWidget(preview_splitter, 4)

        buttons = QHBoxLayout()
        split_button = QPushButton("Poproś Specifiera o podział na slice'y")
        split_button.clicked.connect(lambda: self._request_slice_plan())
        import_button = QPushButton("Wczytaj slices.json")
        import_button.clicked.connect(lambda: self._load_slices_file(force=True))
        send_button = QPushButton("Wyślij kolejne zadanie do Specifiera")
        send_button.clicked.connect(lambda: self._send_next_task())
        reset_button = QPushButton("Zresetuj zadanie")
        reset_button.clicked.connect(lambda: self._reset_selected_task())
        mark_done_button = QPushButton("Oznacz wybrany jako wykonany")
        mark_done_button.clicked.connect(lambda: self._mark_selected_done())
        save_button = QPushButton("Zapisz stan")
        save_button.clicked.connect(lambda: self._save_state())
        clear_button = QPushButton("Wyczyść listę tasków")
        clear_button.clicked.connect(lambda: self._clear_tasks())
        self.unattended_check = QCheckBox("Tryb nienadzorowany: wysyłaj kolejny task po zakończeniu poprzedniego")
        self.unattended_check.stateChanged.connect(lambda: self._save_state())

        buttons.addWidget(split_button)
        buttons.addWidget(import_button)
        buttons.addWidget(send_button)
        buttons.addWidget(reset_button)
        buttons.addWidget(mark_done_button)
        buttons.addWidget(save_button)
        buttons.addWidget(clear_button)
        buttons.addWidget(self.unattended_check)
        buttons.addStretch(1)
        main_layout.addLayout(buttons)

        status_box = QGroupBox("Status agentów")
        status_layout = QGridLayout(status_box)
        for index, role in enumerate(ROLES):
            dot = QLabel()
            dot.setFixedSize(18, 18)
            dot.setStyleSheet("background: #a33; border: 1px solid #222;")
            desc = QLabel(role)
            state = QLabel("nie sprawdzono")
            self.role_labels[role] = state
            status_layout.addWidget(dot, index, 0)
            status_layout.addWidget(desc, index, 1)
            status_layout.addWidget(state, index, 2)
            self.role_labels[f"{role}:dot"] = dot
        main_layout.addWidget(status_box)

        self.setCentralWidget(root)

    def _boxed(self, title: str, widget: QWidget) -> QGroupBox:
        box = QGroupBox(title)
        layout = QVBoxLayout(box)
        layout.addWidget(widget)
        return box

    def _load_state(self) -> None:
        if not self.state_file.exists():
            return
        try:
            data = json.loads(self.state_file.read_text(encoding="utf-8"))
            self.description_editor.setPlainText(data.get("description", ""))
            self.unattended_check.setChecked(bool(data.get("unattended", False)))
            self.tasks = [TaskItem(**item) for item in data.get("tasks", [])]
            if self.slices_file.exists():
                self.loaded_slices_mtime = self.slices_file.stat().st_mtime
        except Exception as exc:
            self._log(f"Nie udało się wczytać stanu GUI: {exc}")

    def _save_state(self) -> None:
        data: dict[str, Any] = {
            "description": self.description_editor.toPlainText(),
            "unattended": self.unattended_check.isChecked(),
            "tasks": [asdict(task) for task in self.tasks],
        }
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        self.state_file.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        self._log("Zapisano stan GUI.")

    def _refresh_task_list(self) -> None:
        current_row = self.task_list.currentRow()
        self.task_list.blockSignals(True)
        self.task_list.clear()
        for task in self.tasks:
            item = QListWidgetItem(f"[{task.state}] {task.title}")
            item.setForeground(self._state_color(task.state))
            self.task_list.addItem(item)
        self.task_list.blockSignals(False)
        if self.tasks:
            self.task_list.setCurrentRow(min(max(current_row, 0), len(self.tasks) - 1))
        else:
            self.task_preview.clear()

    def _state_color(self, state: str) -> QColor:
        if state == "sent":
            return QColor("#b98200")
        if state == "done":
            return QColor("#247a37")
        return QColor("#222222")

    def _show_selected_task(self, row: int) -> None:
        self.task_preview.blockSignals(True)
        if 0 <= row < len(self.tasks):
            self.task_preview.setPlainText(self.tasks[row].body)
        else:
            self.task_preview.clear()
        self.task_preview.blockSignals(False)

    def _update_selected_task_body(self) -> None:
        row = self.task_list.currentRow()
        if 0 <= row < len(self.tasks):
            self.tasks[row].body = self.task_preview.toPlainText()

    def _slice_id(self, title: str, index: int) -> str:
        normalized = unicodedata.normalize("NFKD", title)
        ascii_title = normalized.encode("ascii", "ignore").decode("ascii").lower()
        slug = re.sub(r"[^a-z0-9]+", "-", ascii_title).strip("-")
        return slug or f"slice-{index}"

    def _completion_marker_path(self, task: TaskItem, index: int) -> Path:
        slice_id = task.slice_id or self._slice_id(task.title, index)
        return self.completed_slices_dir / f"{slice_id}.done"

    def _apply_completed_slice_markers(self) -> bool:
        changed = False
        for index, task in enumerate(self.tasks, start=1):
            if task.state == "done":
                continue
            if self._completion_marker_path(task, index).exists():
                task.state = "done"
                changed = True
        if changed:
            self._refresh_task_list()
            self._save_state()
            self._log("Wczytano znaczniki zakończonych slice'ów.")
        return changed

    def _request_slice_plan(self) -> None:
        text = self.description_editor.toPlainText().strip()
        if not text:
            QMessageBox.warning(self, "Brak opisu", "Wklej opis przed wysłaniem do Specifiera.")
            return
        task = TaskItem(
            title="GUI: podział opisu na slice'y",
            body=self._slice_plan_request_body(text),
        )
        self._send_task(task)
        self._save_state()
        self._log("Wysłano opis do Specifiera z prośbą o zapis agent_context/gui/slices.json.")

    def _slice_plan_request_body(self, source: str) -> str:
        return (
            "Task\n"
            "Podziel poniższy opis na małe, inkrementalne slice'y dla GUI operatora.\n\n"
            "Cel:\n"
            "Nie implementuj funkcji i nie przekazuj pracy do Coder. Przygotuj wyłącznie listę slice'ów.\n\n"
            "Opis źródłowy:\n"
            f"{source}\n\n"
            "Wymagany wynik:\n"
            "- przygotuj plan i wyślij go do AntracytowyMaster,\n"
            "- po akceptacji AntracytowyMaster zapisz wynik do agent_context/gui/slices.json,\n"
            "- użyj formatu JSON opisanego w sekcji GUI slice planning protocol w instrukcji Specifiera,\n"
            "- po zapisaniu JSON utwórz agent_context/gui/slices_ready.md,\n"
            "- nie notyfikuj Coder dla tego zadania.\n\n"
            "Oczekiwany styl slice'ów:\n"
            "- każdy slice ma być mały i możliwy do przejścia przez pełny pipeline,\n"
            "- każdy slice ma zawierać pełny tekst zadania, który GUI może później wysłać do Specifiera,\n"
            "- pierwszy slice ma być najmniejszym sensownym krokiem.\n"
        )

    def _load_slices_file(self, force: bool = False) -> None:
        if not self.slices_file.exists():
            if force:
                QMessageBox.information(
                    self,
                    "Brak slices.json",
                    f"Nie znaleziono: {self.slices_file}",
                )
            return
        mtime = self.slices_file.stat().st_mtime
        if not force and mtime <= self.loaded_slices_mtime:
            return
        try:
            data = json.loads(self.slices_file.read_text(encoding="utf-8-sig"))
            slices = data.get("slices", [])
            existing_by_id = {task.slice_id: task for task in self.tasks if task.slice_id}
            existing_by_title = {task.title: task for task in self.tasks}
            existing_by_body = {task.body: task for task in self.tasks}
            loaded: list[TaskItem] = []
            for index, item in enumerate(slices, start=1):
                title = str(item.get("title") or f"Slice {index}")
                slice_id = str(item.get("id") or self._slice_id(title, index))
                body = str(item.get("body") or "").strip()
                if not body:
                    out_of_scope_value = item.get("out_of_scope", [])
                    if isinstance(out_of_scope_value, list):
                        out_of_scope = "\n".join(str(value) for value in out_of_scope_value)
                    else:
                        out_of_scope = str(out_of_scope_value)
                    body = self._task_body(
                        title=title,
                        goal=title,
                        scope=self.description_editor.toPlainText().strip(),
                        out_of_scope=out_of_scope,
                    )
                existing = existing_by_id.get(slice_id) or existing_by_title.get(title) or existing_by_body.get(body)
                if existing:
                    task = TaskItem(title=title, body=body, slice_id=slice_id, state=existing.state, sent_at=existing.sent_at)
                else:
                    task = TaskItem(title=title, body=body, slice_id=slice_id)
                if self._completion_marker_path(task, index).exists():
                    task.state = "done"
                loaded.append(task)
            if not loaded:
                raise ValueError("slices.json nie zawiera listy slices")
            self.tasks = loaded
            self.loaded_slices_mtime = mtime
            self.last_slices_error = ""
            self._refresh_task_list()
            self._save_state()
            self._log(f"Wczytano {len(self.tasks)} slice'ów z {self.slices_file}.")
        except Exception as exc:
            error = str(exc)
            if force or error != self.last_slices_error:
                self._log(f"Nie udało się wczytać slices.json: {error}")
            self.last_slices_error = error
            if force:
                QMessageBox.critical(self, "Błąd slices.json", str(exc))

    def _split_description(self) -> None:
        text = self.description_editor.toPlainText().strip()
        if not text:
            QMessageBox.warning(self, "Brak opisu", "Wklej opis przed rozbiciem na taski.")
            return
        self.tasks = self._build_incremental_tasks(text)
        self._refresh_task_list()
        self._save_state()
        self._log(f"Utworzono {len(self.tasks)} tasków lokalną heurystyką.")

    def _build_incremental_tasks(self, source: str) -> list[TaskItem]:
        if self._looks_like_market_data_mvp(source):
            return self._market_data_mvp_tasks(source)
        chunks = self._paragraph_chunks(source, max_chars=2200)
        tasks = []
        for index, chunk in enumerate(chunks, start=1):
            title = f"Slice {index}: doprecyzowanie i mała implementacja"
            body = self._task_body(
                title=title,
                goal="Przygotuj mały, weryfikowalny slice na podstawie fragmentu opisu.",
                scope=chunk,
            )
            tasks.append(TaskItem(title=title, body=body))
        return tasks

    def _looks_like_market_data_mvp(self, source: str) -> bool:
        lowered = source.lower()
        markers = ["dane/<instrument>", "ts_event", "timeframe", "csv", "instrument"]
        return sum(1 for marker in markers if marker in lowered) >= 3

    def _market_data_mvp_tasks(self, source: str) -> list[TaskItem]:
        definitions = [
            (
                "Slice 1: wykrycie katalogu DANE i instrumentów",
                "Program uruchamiany z cmd wykrywa katalog DANE i wypisuje dostępne instrumenty jako katalogi.",
                "Bez parsowania CSV, bez tabeli rekordów, bez wyboru dat.",
            ),
            (
                "Slice 2: daty i timeframe dla instrumentu",
                "Po wskazaniu instrumentu program pokazuje dostępne timeframe i daty plików.",
                "Bez ładowania danych tick/OHLC do tabeli.",
            ),
            (
                "Slice 3: model instrumentu i wyboru danych",
                "Dodaj model opisu instrumentu oraz kombinacji instrument + data + timeframe.",
                "Bez pełnego parsera CSV i bez GUI.",
            ),
            (
                "Slice 4: parser CSV wymaganych kolumn",
                "Wczytaj format CSV i zapamiętaj wymagane kolumny modelu danych.",
                "Bez optymalizacji pod duże zbiory i bez agregacji OHLC.",
            ),
            (
                "Slice 5: tabela do 20000 rekordów i prezentacja konsolowa",
                "Przechowuj do 20000 rekordów i wyświetl zebrane dane w konsoli.",
                "Bez bazy danych, GUI i pobierania danych z internetu.",
            ),
            (
                "Slice 6: granice modułów i interfejsów",
                "Uporządkuj strukturę modułów tak, aby mechanika programu była oddzielona od danych i IO.",
                "Bez zmiany zachowania zaakceptowanego w poprzednich slice'ach.",
            ),
        ]
        tasks = []
        for title, goal, out_of_scope in definitions:
            body = self._task_body(
                title=title,
                goal=goal,
                scope=source,
                out_of_scope=out_of_scope,
            )
            tasks.append(TaskItem(title=title, body=body))
        return tasks

    def _paragraph_chunks(self, source: str, max_chars: int) -> list[str]:
        paragraphs = [part.strip() for part in source.split("\n\n") if part.strip()]
        chunks: list[str] = []
        current = ""
        for paragraph in paragraphs:
            candidate = f"{current}\n\n{paragraph}".strip()
            if current and len(candidate) > max_chars:
                chunks.append(current)
                current = paragraph
            else:
                current = candidate
        if current:
            chunks.append(current)
        return chunks or [source]

    def _task_body(self, title: str, goal: str, scope: str, out_of_scope: str = "") -> str:
        out_of_scope_text = out_of_scope or "Nie rozszerzaj zakresu poza najmniejszy sensowny slice."
        return (
            "Task\n"
            f"{title}\n\n"
            "Cel:\n"
            f"{goal}\n\n"
            "Opis źródłowy / kontekst:\n"
            f"{scope}\n\n"
            "Oczekiwany efekt Specifiera:\n"
            "- przygotuj specyfikację tego jednego slice'a,\n"
            "- określ kryteria akceptacji,\n"
            "- określ minimalną weryfikację lokalną,\n"
            "- nie uruchamiaj kolejnego slice'a bez osobnego handoffu.\n\n"
            "Poza zakresem:\n"
            f"{out_of_scope_text}\n\n"
            "Ograniczenia:\n"
            "- zachowaj obecny pipeline ról,\n"
            "- praca ma przejść przez Specifier -> Coder -> Cleaner -> Architect -> Hardender -> QA,\n"
            "- nie rozszerzaj implementacji poza zatwierdzony plan.\n"
        )

    def _send_next_task(self) -> None:
        for task in self.tasks:
            if task.state == "pending":
                self._send_task(task)
                self._refresh_task_list()
                self._save_state()
                return
        QMessageBox.information(self, "Brak tasków", "Nie ma tasków w stanie pending.")

    def _mark_selected_done(self) -> None:
        row = self.task_list.currentRow()
        if not (0 <= row < len(self.tasks)):
            QMessageBox.information(self, "Brak wyboru", "Wybierz task albo slice z listy.")
            return
        self.tasks[row].state = "done"
        if not self.tasks[row].sent_at:
            self.tasks[row].sent_at = datetime.now().isoformat(timespec="seconds")
        title = self.tasks[row].title
        marker = self._completion_marker_path(self.tasks[row], row + 1)
        marker.write_text(
            f"completed_at={datetime.now().isoformat(timespec='seconds')}\nsource=OperatorGui\n",
            encoding="utf-8",
        )
        self._refresh_task_list()
        self.task_list.setCurrentRow(row)
        self._save_state()
        self._log(f"Oznaczono jako wykonany: {title}; marker: {marker.name}")

    def _reset_selected_task(self) -> None:
        row = self.task_list.currentRow()
        if not (0 <= row < len(self.tasks)):
            QMessageBox.information(self, "Brak wyboru", "Wybierz task albo slice z listy.")
            return

        task = self.tasks[row]
        answer = QMessageBox.question(
            self,
            "Reset zadania",
            f"Ustawic '{task.title}' ponownie jako pending i wyczyscic czas wysylki?",
        )
        if answer != QMessageBox.StandardButton.Yes:
            return

        marker = self._completion_marker_path(task, row + 1)
        if marker.exists():
            marker.unlink()
        task.state = "pending"
        task.sent_at = ""
        self.activity_seen_after_send = False
        self._refresh_task_list()
        self.task_list.setCurrentRow(row)
        self._save_state()
        self._log(f"Zresetowano zadanie do pending: {task.title}")

    def _send_task(self, task: TaskItem) -> None:
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S.%f")[:-3]
        message_path = self.outbox_dir / f"{stamp}.md"
        message = (
            "FROM: OperatorGui\n"
            "TO: Specifier\n"
            "TYPE: TASK\n"
            f"TASK: gui_{stamp}\n"
            "CONTEXT:\n"
            f"{task.body}\n\n"
            "EXPECTED_OUTPUT:\n"
            "Create or refine the next specification slice for this project.\n\n"
            "CONSTRAINTS:\n"
            "Work only within the Specifier role. Do not expand scope.\n"
        )
        message_path.write_text(message, encoding="utf-8")

        script = self.project_root / "scripts" / "send_to_role_psmux_separate_windows_clean.cmd"
        env = os.environ.copy()
        env["SWARM_PROJECT_ROOT"] = str(self.project_root)
        result = subprocess.run(
            ["cmd", "/c", str(script), "Specifier", "/file", str(message_path)],
            cwd=self.project_root,
            env=env,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            self._log(f"Wysyłka nieudana: {result.stderr or result.stdout}")
            QMessageBox.critical(self, "Błąd wysyłki", result.stderr or result.stdout)
            return
        task.state = "sent"
        task.sent_at = datetime.now().isoformat(timespec="seconds")
        self.activity_seen_after_send = False
        self._log(f"Wysłano do Specifiera: {task.title}")

    def _tick(self) -> None:
        self._load_slices_file()
        self._apply_completed_slice_markers()
        self._refresh_agent_status()
        completed_sent_task = self._mark_sent_task_done_after_activity()
        if completed_sent_task and self.unattended_check.isChecked():
            self._send_next_task()

    def _refresh_agent_status(self) -> None:
        pane_map = self._read_pane_map()
        any_working = False
        any_inbox = False
        for role in ROLES:
            role_root = self.project_root / "agent_context" / "roles" / role
            inbox_count = self._file_count(role_root / "inbox")
            working_count = self._file_count(role_root / "working")
            connected = self._role_connected(role, pane_map)
            any_working = any_working or working_count > 0
            any_inbox = any_inbox or inbox_count > 0

            if working_count:
                self._set_role_status(role, "#d6a400", f"pracuje ({working_count} w working)")
            elif connected:
                self._set_role_status(role, "#2a9d45", f"gotowy, inbox: {inbox_count}")
            else:
                self._set_role_status(role, "#b13a2f", "brak połączenia / brak sesji")
        self.any_role_working = any_working
        self.any_role_inbox = any_inbox

    def _read_pane_map(self) -> dict[str, str]:
        path = self.project_root / ".swarmforge" / "panes.env"
        values: dict[str, str] = {}
        if not path.exists():
            return values
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            if "=" in line:
                key, value = line.split("=", 1)
                values[key.strip()] = value.strip()
        return values

    def _role_connected(self, role: str, pane_map: dict[str, str]) -> bool:
        return bool(
            pane_map.get(f"{role}_NAMESPACE")
            and pane_map.get(f"{role}_SESSION")
            and pane_map.get(f"{role}_TARGET")
        )

    def _file_count(self, path: Path) -> int:
        if not path.exists():
            return 0
        return sum(1 for item in path.iterdir() if item.is_file())

    def _set_role_status(self, role: str, color: str, text: str) -> None:
        self.role_labels[f"{role}:dot"].setStyleSheet(
            f"background: {color}; border: 1px solid #222;"
        )
        self.role_labels[role].setText(text)

    def _mark_sent_task_done_after_activity(self) -> bool:
        sent_task = next((task for task in self.tasks if task.state == "sent"), None)
        if sent_task is None:
            return False
        if self.any_role_working or self.any_role_inbox:
            self.activity_seen_after_send = True
            return False
        if self.activity_seen_after_send and self._final_role_done_after_task_sent(sent_task):
            sent_task.state = "done"
            self.activity_seen_after_send = False
            self._refresh_task_list()
            self._save_state()
            self._log("Oznaczono wyslany slice jako wykonany po zakonczeniu roli QA.")
            return True
        return False

    def _final_role_done_after_task_sent(self, task: TaskItem) -> bool:
        if not task.sent_at:
            return False
        try:
            sent_at = datetime.fromisoformat(task.sent_at).timestamp()
        except ValueError:
            return False
        done_dir = self.project_root / "agent_context" / "roles" / "QA" / "done"
        if not done_dir.exists():
            return False
        return any(item.is_file() and item.stat().st_mtime >= sent_at for item in done_dir.iterdir())

    def _clear_tasks(self) -> None:
        answer = QMessageBox.question(
            self,
            "Wyczyścić listę?",
            "Usunąć lokalną listę tasków z GUI? Nie usuwa to wysłanych handoffów.",
        )
        if answer != QMessageBox.StandardButton.Yes:
            return
        self.tasks = []
        self._refresh_task_list()
        self._save_state()

    def _log(self, message: str) -> None:
        stamp = datetime.now().strftime("%H:%M:%S")
        self.log_view.append(f"[{stamp}] {message}")


def find_project_root(start: Path) -> Path:
    current = start.resolve()
    while True:
        if (current / ".swarm_project_root").exists():
            return current
        if current.parent == current:
            raise RuntimeError("Could not find .swarm_project_root")
        current = current.parent


def main() -> int:
    try:
        project_root = find_project_root(Path.cwd())
    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    app = QApplication(sys.argv)
    window = SwarmForgeTaskSender(project_root)
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
