# mutation-stamp: sha256=6de5ccc851095ef15cc203a92ab03431a36ae983eb827f0687313fb5f88f6706
# acceptance-mutation-manifest-begin
# {"version":1,"tested_at":"2026-07-14T19:32:37Z","feature_name":"Console timeframe date discovery","feature_path":"acceptance\\features\\console_timeframe_date_discovery.feature","background_hash":"f3e98878efff11a6032b82f277d9ab490b97d2361b48a02195d96c0c57ae10ca","implementation_hash":"unknown","scenarios":[]}
# acceptance-mutation-manifest-end

# Console timeframe date discovery 001
Feature: Console timeframe date discovery
  The console application reports timeframes and file dates for a selected local instrument.

  Background:
    Given the application is started from the project root
    And the local data directory "DANE" is available

  # Console timeframe date discovery 001
  Scenario: Console timeframe date discovery 001 lists timeframes for the selected instrument
    Given the local data directory contains instrument "MESM6" with timeframe directories:
      | timeframe |
      | tick      |
      | 1s        |
    And the local data directory contains instrument "NQMM6" with timeframe directories:
      | timeframe |
      | 5s        |
    When the user runs the console application
    And the user selects instrument "MESM6"
    Then the console output lists the available timeframes for "MESM6":
      | timeframe |
      | tick      |
      | 1s        |
    And the console output does not list "5s" as a timeframe for "MESM6"
    And the console output does not show CSV records

  # Console timeframe date discovery 002
  Scenario: Console timeframe date discovery 002 normalizes dates from filenames for the selected instrument
    Given the local data directory contains files for instrument "MESM6":
      | timeframe | filename                       |
      | tick      | glbx-mdp3-20260501.trades.csv  |
      | 1s        | glbx-mdp3-2026-05-03.ohlc.csv  |
    When the user runs the console application
    And the user selects instrument "MESM6"
    Then the console output lists the available dates for "MESM6":
      | date       |
      | 2026-05-01 |
      | 2026-05-03 |
    And the console output does not read CSV contents

  # Console timeframe date discovery 003
  Scenario: Console timeframe date discovery 003 ignores filenames without date tokens
    Given the local data directory contains files for instrument "MESM6":
      | timeframe | filename                      |
      | tick      | glbx-mdp3-20260501.trades.csv |
      | tick      | notes.csv                     |
    When the user runs the console application
    And the user selects instrument "MESM6"
    Then the console output lists the available dates for "MESM6":
      | date       |
      | 2026-05-01 |
    And the console output does not list "notes.csv" as a date

  # Console timeframe date discovery 004
  Scenario: Console timeframe date discovery 004 reports no timeframes for an empty instrument directory
    Given the local data directory contains instrument "MESM6" with no timeframe directories
    When the user runs the console application
    And the user selects instrument "MESM6"
    Then the console output reports that no timeframes are available for "MESM6"
    And the console application exits without a traceback
