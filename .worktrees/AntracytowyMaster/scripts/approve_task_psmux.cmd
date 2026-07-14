@echo off
for %%I in ("%~dp0..") do set "SWARM_PROJECT_ROOT=%%~fI"
call "%SWARM_PROJECT_ROOT%\..\..\scripts\approve_task_psmux.cmd" %*
