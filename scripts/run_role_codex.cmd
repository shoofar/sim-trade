@echo off
setlocal EnableExtensions
for %%I in ("%~dp0..") do set "SWARM_PROJECT_ROOT=%%~fI"

set "ROLE=%~1"
if not defined SWARM_ROLE_START_STAGGER_SECONDS set "SWARM_ROLE_START_STAGGER_SECONDS=3"
call :RoleStartOffset "%ROLE%"
set /a "START_DELAY=ROLE_START_OFFSET * SWARM_ROLE_START_STAGGER_SECONDS"
if %START_DELAY% GTR 0 (
  echo Delaying %ROLE% Codex startup by %START_DELAY% seconds to stagger MCP initialization...
  timeout /t %START_DELAY% /nobreak >nul
)

call "%SWARM_PROJECT_ROOT%\..\..\scripts\run_role_codex.cmd" %*
exit /b %ERRORLEVEL%

:RoleStartOffset
set "ROLE_START_OFFSET=0"
if /I "%~1"=="Specifier" set "ROLE_START_OFFSET=0"
if /I "%~1"=="Coder" set "ROLE_START_OFFSET=1"
if /I "%~1"=="Cleaner" set "ROLE_START_OFFSET=2"
if /I "%~1"=="Architect" set "ROLE_START_OFFSET=3"
if /I "%~1"=="Hardender" set "ROLE_START_OFFSET=4"
if /I "%~1"=="QA" set "ROLE_START_OFFSET=5"
if /I "%~1"=="AntracytowyMaster" set "ROLE_START_OFFSET=6"
exit /b 0
