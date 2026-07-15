# Swarm-Forge-3.0

This repository defines the Swarm-Forge-3.0 operating model.

## Scope

- `control/` contains role instructions.
- `control/standards/acceptance-pipeline-specification/` contains the local, refreshable snapshot of the Acceptance Pipeline Specification.
- `Engineering.md` contains the shared engineering rules for all roles.
- `Project.md` contains project-local SwarmForge rules for this version.
- `Communication.md` contains the role communication pipeline.
- `Layout.md` contains the intended directory layout.
- `projects/` contains independent project workspaces.
- Root-level instructions apply to the whole Swarm-Forge-3.0 tree unless a nested `AGENTS.md` overrides them.

## Working model

- The system is organized around roles with explicit responsibilities.
- Role instructions must remain strict and non-overlapping.
- A role may only do work that belongs to that role.
- When a task belongs elsewhere, redirect it to the correct role instead of expanding scope.

## Pipeline

The default role pipeline is:

```text
Specifier -> Coder -> Cleaner -> Architect -> Hardender -> QA
```

If `PIPELINE.md` does not define a different active flow, agents must use the flow defined in this file.

Each role in the pipeline must create a plan, send it to `AntracytowyMaster` for approval, and only execute the plan after approval.

## Shared rules

- All roles must obey `Engineering.md`.
- All roles must obey `Project.md`.
- All roles must obey `Communication.md`.
- All roles must obey `Layout.md`.
- On startup, after reading role instructions and operating rules, an agent checks `agent_context/roles/<role>/inbox/` for pending tasks.
- If a pending task exists, the agent moves the oldest pending message to `agent_context/roles/<role>/working/`.
- The agent processes the task from `agent_context/roles/<role>/working/`.
- If work becomes blocked, the agent must stop active execution, write a blocker report with the reason, evidence, and required unblock action, and leave the task message in `agent_context/roles/<role>/working/`.
- Blocked tasks must not be moved to `agent_context/roles/<role>/done/`; keeping them in `working/` is required so the role can resume the same task after the blocker is removed.

## Long-running interactive programs

- Specifier must define deterministic test boundaries for any console, daemon, watcher, server, or other long-running interactive program.
- Coder must implement long-running interaction so production can wait for operator input, but automated tests must terminate through an explicit command, EOF, timeout, or bounded step count.
- Tests must not mock input with an infinite constant response, and must not run an interactive subprocess with captured output unless they send a terminating input such as `quit` or close stdin and enforce a timeout.
- Prefer testing interaction through a bounded session/state-machine API such as `handle_input(line)` or a `max_steps` test hook; keep full subprocess E2E tests minimal, timeout-protected, and responsible for killing the process on failure.
- Acceptance criteria for long-running behavior must verify both liveness and deterministic shutdown, so stdout capture cannot grow without bound and Codex/CLI runners cannot wait forever.
- Before handoff, an agent that started test processes, subprocesses, servers, watchers, CLIs, or other child processes must stop every process it started or prove that it exited. If a launched command can orphan children, the agent must fix the invoking code/script/test to use timeouts, process cleanup, and child termination before handing off.

## Priority

- Nested `AGENTS.md` files override this file within their subtree.
- Project-specific instructions, when added later under `projects/<name>/`, will override root guidance for that project.
