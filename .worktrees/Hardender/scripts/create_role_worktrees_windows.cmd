@echo off
for %%I in ("%~dp0..") do set "SWARM_PROJECT_ROOT=%%~fI"
call "%SWARM_PROJECT_ROOT%\..\..\scripts\create_role_worktrees_windows.cmd" %*
