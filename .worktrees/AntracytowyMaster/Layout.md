# Layout

## Root

- `AGENTS.md`
- `Engineering.md`
- `Project.md`
- `Communication.md`
- `README.md`
- `.swarmforge/`
- `.worktrees/`
- `agent_context/`
- `logs/`
- `swarmtools/`
- `control/`
- `projects/`
- `scripts/`

## Control

- `control/AGENTS.md`
- `control/standards/acceptance-pipeline-specification/`
- `control/roles/AntracytowyMaster/`
- `control/roles/Specifier/`
- `control/roles/Coder/`
- `control/roles/Cleaner/`
- `control/roles/Architect/`
- `control/roles/Hardender/`
- `control/roles/QA/`

## Roles

Each role directory should contain:

- `AGENTS.md`
- `AGENT_PROMPT.md`

## Projects

- `projects/<project-name>/`

Each project should keep its own local state, scripts, worktrees, logs, and project files under that directory, including:

- `workspace/`
- `.swarmforge/`
- `.worktrees/`
- `agent_context/`
- `logs/`
- `swarmtools/`
- `scripts/`

## Scripts

- `scripts/` contains project bootstrap and maintenance scripts for this version.

## Shared Context

- `agent_context/roles/<role>/inbox/`
- `agent_context/roles/<role>/working/`
- `agent_context/roles/<role>/done/`
- `agent_context/messages/`

## Local State

- `.swarmforge/` contains project-local swarm state.
- `.swarmforge/inputs/` contains input artifacts.
- `.swarmforge/hardening/` contains local hardening tools and state.
- `.swarmforge/security_reports/` contains hardening and verification reports.
- `.worktrees/` contains role worktrees.
- `logs/` contains operational logs.
- `swarmtools/` contains helper scripts and project tooling.
