# Local Hardener Toolchain

Use this toolchain when Hardender needs local, installable evidence during later slices.

## Contents

- `crap4python` from `projects\crap4python`
- `mutate4python` from `projects\mutate4python`
- `radon`, `ruff`, `bandit`, `mutmut`, and `pytest-timeout` installed into `.swarmforge\hardening\.venv-tools`
- `jscpd` installed into `.swarmforge\hardening\node-tools` when Node.js/npm is available

## Install

From the Swarm-Forge-3.0 root:

```cmd
swarmtools\install_hardener_tools.cmd
```

This creates or updates:

```text
.swarmforge\hardening\.venv-tools
.swarmforge\hardening\node-tools
.swarmforge\hardening\hardening_env.cmd
```

The installer does not install global Python packages, does not use editable installs, and does not install Node.js. If `npm` is missing, `jscpd` is skipped with a warning; install Node.js/npm and rerun the script when duplicate-code detection is required.

## Run

After installation, use the dedicated project-local commands:

```cmd
.swarmforge\hardening\.venv-tools\Scripts\crap4python.exe --help
.swarmforge\hardening\.venv-tools\Scripts\mutate4python.exe --help
.swarmforge\hardening\.venv-tools\Scripts\radon.exe cc src
.swarmforge\hardening\.venv-tools\Scripts\ruff.exe check src
.swarmforge\hardening\.venv-tools\Scripts\bandit.exe -r src
.swarmforge\hardening\.venv-tools\Scripts\mutmut.exe --help
.swarmforge\hardening\.venv-tools\Scripts\pytest.exe --timeout=30
.swarmforge\hardening\node-tools\node_modules\.bin\jscpd.cmd src --reporters console
```

For a short-command shell session, first load the local hardening environment:

```cmd
call .swarmforge\hardening\hardening_env.cmd
radon cc src
ruff check src
bandit -r src
pytest --timeout=30
jscpd src --reporters console
go version
```

Do not require these commands to be present in the global PATH. They are valid when resolved through the project-local paths above or after calling `hardening_env.cmd`.

On Windows, `mutmut.exe` is only an installation check. Real mutation-test runs must use WSL.

For slice hardening, run the installed tools against the same target and keep full stdout/stderr in `.swarmforge\security_reports\<task_id>\`.

## Rule

If the toolchain is missing or broken, install it with `swarmtools\install_hardener_tools.cmd` before reporting the slice result.
