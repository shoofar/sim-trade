# Project Rules

- This project is configured for SwarmForge with seven Codex-backed agents: specifier, coder, cleaner, architect, hardender, QA, and AntracytowyMaster.
- Project language: python, pytest where feasible.
- Keep swarm state local under this project's `.swarmforge/`, worktrees under this project's `.worktrees/`, local wrapper scripts under `scripts/`, helper scripts under `swarmtools/`, logs under `logs/`, and shared agent context under `agent_context/`.
- Keep project-local state isolated within this project tree.
- Prefer terse, explicit handoffs that report state and request role-appropriate review. Do not include verifications or sender process narrative.
- Do not change another role's prompt or workflow ownership without explicit user direction.
