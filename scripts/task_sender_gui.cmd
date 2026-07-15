@echo off
for %%I in ("%~dp0..") do set "SWARM_PROJECT_ROOT=%%~fI"

set "PYTHON_CMD="
where python >nul 2>nul
if not errorlevel 1 set "PYTHON_CMD=python"
if not defined PYTHON_CMD (
  where py >nul 2>nul
  if not errorlevel 1 set "PYTHON_CMD=py"
)
if not defined PYTHON_CMD (
  echo ERROR: Python was not found in PATH.
  exit /b 1
)

%PYTHON_CMD% -c "import PyQt6" >nul 2>nul
if errorlevel 1 (
  echo ERROR: PyQt6 is not installed for the active Python.
  echo Install it with:
  echo   %PYTHON_CMD% -m pip install PyQt6
  exit /b 1
)

%PYTHON_CMD% "%SWARM_PROJECT_ROOT%\swarmtools\task_sender_gui.py" %*
exit /b %ERRORLEVEL%
