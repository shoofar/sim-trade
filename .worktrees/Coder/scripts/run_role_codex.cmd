@echo off
for %%I in ("%~dp0..") do set "SWARM_PROJECT_ROOT=%%~fI"
call "%SWARM_PROJECT_ROOT%\..\..\scripts\run_role_codex.cmd" %*
