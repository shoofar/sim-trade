# Local Hardener Toolchain

Use this toolchain when Hardender needs local, installable evidence during later slices.

## Contents

- `crap4python` from `projects\crap4python`
- `dry4python` from `projects\dry4python`
- `mutate4python` from `projects\mutate4python`

## Install

From the Swarm-Forge-2.0 root:

```cmd
swarmtools\install_hardener_tools.cmd
```

This creates:

```text
.swarmforge\hardening\.venv-tools
```

## Run

After installation, use the dedicated venv commands:

```cmd
.swarmforge\hardening\.venv-tools\Scripts\crap4python.exe --help
.swarmforge\hardening\.venv-tools\Scripts\dry4python.exe --help
.swarmforge\hardening\.venv-tools\Scripts\mutate4python.exe --help
```

For slice hardening, run both tools against the same target and keep full stdout/stderr in `.swarmforge\security_reports\<task_id>\`.

## Rule

If the toolchain is missing or broken, install it with `swarmtools\install_hardener_tools.cmd` before reporting the slice result.

