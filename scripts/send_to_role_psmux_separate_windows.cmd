@echo off
for %%I in ("%~dp0..") do set "SWARM_PROJECT_ROOT=%%~fI"
call "%SWARM_PROJECT_ROOT%\..\..\scripts\send_to_role_psmux_separate_windows.cmd" %*
