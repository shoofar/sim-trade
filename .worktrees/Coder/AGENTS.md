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

## Priority

- Nested `AGENTS.md` files override this file within their subtree.
- Project-specific instructions, when added later under `projects/<name>/`, will override root guidance for that project.
