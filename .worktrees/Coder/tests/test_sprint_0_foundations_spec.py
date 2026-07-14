from pathlib import Path


WORKTREE_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = Path(__file__).resolve().parents[3]
FEATURE_FILE = WORKTREE_ROOT / "tests" / "features" / "sprint_0_foundations.feature"
QA_FILE = WORKTREE_ROOT / "tests" / "qa" / "sprint_0_foundations_qa.md"
DANE_FILE = PROJECT_ROOT / "DANE" / "MESM" / "RAW" / "glbx-mdp3-20260501.trades.csv"


def test_sprint_0_visible_spec_matches_the_current_dane_surface():
    feature_text = FEATURE_FILE.read_text(encoding="utf-8")
    qa_text = QA_FILE.read_text(encoding="utf-8")

    assert FEATURE_FILE.exists()
    assert QA_FILE.exists()
    assert DANE_FILE.exists()

    assert "DANE/<instrument>" in feature_text
    assert "MESM" in feature_text
    assert "2026-05-01" in feature_text
    assert "trades" in feature_text
    assert "Given, When, and Then" in feature_text

    assert "MESM" in qa_text
    assert "2026-05-01" in qa_text
    assert "trades" in qa_text
    assert "user-visible behavior" in qa_text
