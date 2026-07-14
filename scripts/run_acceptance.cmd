@echo off
setlocal
for %%I in ("%~dp0..") do set "CODE_ROOT=%%~fI"
if "%SWARM_PROJECT_ROOT%"=="" (
  set "STATE_ROOT=%CODE_ROOT%"
) else (
  set "STATE_ROOT=%SWARM_PROJECT_ROOT%"
)
set "PARSER=%STATE_ROOT%\.swarmforge\hardening\bin\gherkin-parser.exe"
if not exist "%PARSER%" (
  echo missing APS gherkin-parser: %PARSER%
  exit /b 1
)
if not exist "%CODE_ROOT%\build\acceptance\ir" mkdir "%CODE_ROOT%\build\acceptance\ir"
if not exist "%CODE_ROOT%\acceptance\generated" mkdir "%CODE_ROOT%\acceptance\generated"
"%PARSER%" "%CODE_ROOT%\acceptance\features\console_instrument_discovery.feature" "%CODE_ROOT%\build\acceptance\ir\console_instrument_discovery.json" || exit /b 1
"%PARSER%" "%CODE_ROOT%\acceptance\features\console_timeframe_date_discovery.feature" "%CODE_ROOT%\build\acceptance\ir\console_timeframe_date_discovery.json" || exit /b 1
"%PARSER%" "%CODE_ROOT%\acceptance\features\console_selection_memory.feature" "%CODE_ROOT%\build\acceptance\ir\console_selection_memory.json" || exit /b 1
"%PARSER%" "%CODE_ROOT%\acceptance\features\console_instrument_description.feature" "%CODE_ROOT%\build\acceptance\ir\console_instrument_description.json" || exit /b 1
pushd "%CODE_ROOT%" || exit /b 1
python -m acceptance.generate_acceptance "%CODE_ROOT%\build\acceptance\ir\console_instrument_discovery.json" "%CODE_ROOT%\acceptance\generated\test_console_instrument_discovery.py" || exit /b 1
python -m acceptance.generate_acceptance "%CODE_ROOT%\build\acceptance\ir\console_timeframe_date_discovery.json" "%CODE_ROOT%\acceptance\generated\test_console_timeframe_date_discovery.py" || exit /b 1
python -m acceptance.generate_acceptance "%CODE_ROOT%\build\acceptance\ir\console_selection_memory.json" "%CODE_ROOT%\acceptance\generated\test_console_selection_memory.py" || exit /b 1
python -m acceptance.generate_acceptance "%CODE_ROOT%\build\acceptance\ir\console_instrument_description.json" "%CODE_ROOT%\acceptance\generated\test_console_instrument_description.py" || exit /b 1
python -m pytest "%CODE_ROOT%\acceptance\generated" || exit /b 1
