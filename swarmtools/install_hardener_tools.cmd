@echo off
setlocal EnableExtensions EnableDelayedExpansion

set "SCRIPT_DIR=%~dp0"
for %%I in ("%SCRIPT_DIR%..") do set "PROJECT_ROOT=%%~fI"
set "TOOLS_VENV=%PROJECT_ROOT%\.swarmforge\hardening\.venv-tools"
set "NODE_TOOLS=%PROJECT_ROOT%\.swarmforge\hardening\node-tools"
set "HARDENING_ENV=%PROJECT_ROOT%\.swarmforge\hardening\hardening_env.cmd"
set "LOCAL_GO=%PROJECT_ROOT%\.swarmforge\hardening\go1.26.5\go"
set "CRAP_PROJECT=%PROJECT_ROOT%\projects\crap4python"
set "MUTATE_PROJECT=%PROJECT_ROOT%\projects\mutate4python"
if not exist "%CRAP_PROJECT%\pyproject.toml" (
  for %%I in ("%PROJECT_ROOT%\..\crap4python") do set "CRAP_PROJECT=%%~fI"
)
if not exist "%MUTATE_PROJECT%\pyproject.toml" (
  for %%I in ("%PROJECT_ROOT%\..\mutate4python") do set "MUTATE_PROJECT=%%~fI"
)

if not exist "%CRAP_PROJECT%\pyproject.toml" (
  echo ERROR: Missing project: %CRAP_PROJECT%
  exit /b 1
)
if not exist "%MUTATE_PROJECT%\pyproject.toml" (
  echo ERROR: Missing project: %MUTATE_PROJECT%
  exit /b 1
)

set "PYTHON_EXE="
set "PYTHON_ARGS="
for /f "delims=" %%P in ('where python 2^>nul') do if not defined PYTHON_EXE set "PYTHON_EXE=%%P"
if not defined PYTHON_EXE (
  if exist "%LocalAppData%\Programs\Python\Python311\python.exe" set "PYTHON_EXE=%LocalAppData%\Programs\Python\Python311\python.exe"
)
if not defined PYTHON_EXE (
  for /f "delims=" %%P in ('where py 2^>nul') do if not defined PYTHON_EXE set "PYTHON_EXE=%%P" & set "PYTHON_ARGS=-3"
)
if not defined PYTHON_EXE (
  echo ERROR: Neither python nor py was found in PATH.
  exit /b 1
)

if not exist "%TOOLS_VENV%\Scripts\python.exe" (
  "%PYTHON_EXE%" %PYTHON_ARGS% -m venv "%TOOLS_VENV%"
  if errorlevel 1 (
    echo ERROR: Could not create virtual environment: %TOOLS_VENV%
    exit /b 1
  )
)

set "VENV_PY=%TOOLS_VENV%\Scripts\python.exe"
"%VENV_PY%" -m pip install --upgrade pip wheel
if errorlevel 1 (
  echo ERROR: Could not upgrade pip and wheel in local hardening venv.
  exit /b 1
)

"%VENV_PY%" -m pip install --no-cache-dir --no-build-isolation --force-reinstall radon ruff bandit mutmut pytest-timeout "%CRAP_PROJECT%" "%MUTATE_PROJECT%"
if errorlevel 1 (
  echo ERROR: Could not install local hardening tools into the project venv.
  exit /b 1
)

for %%P in (crap4python mutate4python) do (
  for /d %%D in ("%TOOLS_VENV%\Lib\site-packages\%%P-*.dist-info") do (
    if exist "%%~fD\direct_url.json" del /q "%%~fD\direct_url.json"
  )
)

set "NPM_CMD="
set "NODE_EXE="
set "LOCAL_NODE_BIN=%NODE_TOOLS%\node_modules\.bin"
for /f "delims=" %%N in ('where npm 2^>nul') do if not defined NPM_CMD set "NPM_CMD=%%N"
if not defined NPM_CMD if exist "%ProgramFiles%\nodejs\npm.cmd" set "NPM_CMD=%ProgramFiles%\nodejs\npm.cmd"
if not defined NPM_CMD if exist "%ProgramFiles(x86)%\nodejs\npm.cmd" set "NPM_CMD=%ProgramFiles(x86)%\nodejs\npm.cmd"
for /f "delims=" %%N in ('where node 2^>nul') do if not defined NODE_EXE set "NODE_EXE=%%N"
if not defined NODE_EXE if exist "%ProgramFiles%\nodejs\node.exe" set "NODE_EXE=%ProgramFiles%\nodejs\node.exe"
if not defined NODE_EXE if exist "%ProgramFiles(x86)%\nodejs\node.exe" set "NODE_EXE=%ProgramFiles(x86)%\nodejs\node.exe"
if defined NPM_CMD (
  call "%NPM_CMD%" install --prefix "%NODE_TOOLS%" jscpd
  if errorlevel 1 (
    echo ERROR: Could not install project-local jscpd with npm.
    exit /b 1
  )
  if defined NODE_EXE (
    if not exist "%LOCAL_NODE_BIN%" mkdir "%LOCAL_NODE_BIN%"
    copy /Y "%NODE_EXE%" "%LOCAL_NODE_BIN%\node.exe" >nul
    if errorlevel 1 (
      echo ERROR: Could not copy node.exe into the project-local jscpd bin directory.
      exit /b 1
    )
  ) else (
    echo WARNING: node.exe was not found. jscpd may require global Node.js at runtime.
  )
) else (
  echo WARNING: npm was not found. Project-local jscpd was not installed.
  echo WARNING: Install Node.js/npm and rerun this script if DRY duplicate detection is required.
)

(
  echo @echo off
  echo set "PROJECT_ROOT=%PROJECT_ROOT%"
  echo set "TOOLS_VENV=%TOOLS_VENV%"
  echo set "NODE_TOOLS=%NODE_TOOLS%"
  if exist "%LOCAL_NODE_BIN%\node.exe" echo set "NODE_BIN=%LOCAL_NODE_BIN%"
  if exist "%LOCAL_GO%\bin\go.exe" echo set "GOROOT=%LOCAL_GO%"
  if exist "%PROJECT_ROOT%\.swarmforge\hardening\gopath" echo set "GOPATH=%PROJECT_ROOT%\.swarmforge\hardening\gopath"
  if exist "%PROJECT_ROOT%\.swarmforge\hardening\gocache" echo set "GOCACHE=%PROJECT_ROOT%\.swarmforge\hardening\gocache"
  if exist "%PROJECT_ROOT%\.swarmforge\hardening\gomodcache" echo set "GOMODCACHE=%PROJECT_ROOT%\.swarmforge\hardening\gomodcache"
  if exist "%LOCAL_GO%\bin\go.exe" (
    if exist "%LOCAL_NODE_BIN%\node.exe" (
      echo set "PATH=%TOOLS_VENV%\Scripts;%LOCAL_NODE_BIN%;%LOCAL_GO%\bin;%%PATH%%"
    ) else (
      echo set "PATH=%TOOLS_VENV%\Scripts;%NODE_TOOLS%\node_modules\.bin;%LOCAL_GO%\bin;%%PATH%%"
    )
  ) else (
    if exist "%LOCAL_NODE_BIN%\node.exe" (
      echo set "PATH=%TOOLS_VENV%\Scripts;%LOCAL_NODE_BIN%;%%PATH%%"
    ) else (
      echo set "PATH=%TOOLS_VENV%\Scripts;%NODE_TOOLS%\node_modules\.bin;%%PATH%%"
    )
  )
) > "%HARDENING_ENV%"

echo Installed local hardening tools into:
echo   %TOOLS_VENV%
echo Installed Python hardening backends into the project venv:
echo   radon ruff bandit mutmut pytest-timeout
if defined NPM_CMD (
  echo Installed project-local Node.js duplicate detector into:
  echo   %NODE_TOOLS%
)
echo Wrote local hardening environment:
echo   %HARDENING_ENV%
exit /b 0
