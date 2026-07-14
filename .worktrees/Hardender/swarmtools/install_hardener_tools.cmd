@echo off
setlocal EnableExtensions EnableDelayedExpansion

set "SCRIPT_DIR=%~dp0"
for %%I in ("%SCRIPT_DIR%..") do set "PROJECT_ROOT=%%~fI"
set "TOOLS_VENV=%PROJECT_ROOT%\.swarmforge\hardening\.venv-tools"
set "CRAP_PROJECT=%PROJECT_ROOT%\projects\crap4python"
set "DRY_PROJECT=%PROJECT_ROOT%\projects\dry4python"
set "MUTATE_PROJECT=%PROJECT_ROOT%\projects\mutate4python"

if not exist "%CRAP_PROJECT%\pyproject.toml" (
  echo ERROR: Missing project: %CRAP_PROJECT%
  exit /b 1
)
if not exist "%DRY_PROJECT%\pyproject.toml" (
  echo ERROR: Missing project: %DRY_PROJECT%
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
"%VENV_PY%" -m pip install -e "%CRAP_PROJECT%" -e "%DRY_PROJECT%" -e "%MUTATE_PROJECT%"
if errorlevel 1 (
  echo ERROR: Could not install local hardening tools.
  exit /b 1
)

echo Installed local hardening tools into:
echo   %TOOLS_VENV%
exit /b 0

