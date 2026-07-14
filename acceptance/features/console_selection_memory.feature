# Console selection memory 001
Feature: Console selection memory
  The console application remembers the user's selected instrument and date during the current run.

  Background:
    Given the application is started from the project root
    And the local data directory "DANE" is available
    And available instruments, timeframes, and dates have been discovered from local filenames

  # Console selection memory 001
  Scenario: Console selection memory 001 stores a valid instrument and date selection
    Given instrument "MESM6" has available date "2026-05-01"
    When the user runs the console application
    And the user selects instrument "MESM6"
    And the user selects date "2026-05-01"
    Then the application stores a selection table row:
      | instrument | date       |
      | MESM6      | 2026-05-01 |
    And the console output confirms the stored selection "MESM6" and "2026-05-01"
    And the console output does not show CSV records

  # Console selection memory 002
  Scenario: Console selection memory 002 rejects a date that was not discovered for the selected instrument
    Given instrument "MESM6" has available date "2026-05-01"
    When the user runs the console application
    And the user selects instrument "MESM6"
    And the user selects date "2026-05-02"
    Then the console output rejects date "2026-05-02" for instrument "MESM6"
    And the application does not store a selection table row for "MESM6" and "2026-05-02"
    And the console application exits without a traceback

  # Console selection memory 003
  Scenario: Console selection memory 003 rejects an instrument that was not discovered
    Given instrument "MESM6" has available date "2026-05-01"
    When the user runs the console application
    And the user selects instrument "NQMM6"
    Then the console output rejects instrument "NQMM6"
    And the application does not store a selection table row for "NQMM6"
    And the console application exits without a traceback

  # Console selection memory 004
  Scenario: Console selection memory 004 keeps selections only for the current run
    Given instrument "MESM6" has available date "2026-05-01"
    When the user runs the console application
    And the user selects instrument "MESM6"
    And the user selects date "2026-05-01"
    Then the application stores a selection table row:
      | instrument | date       |
      | MESM6      | 2026-05-01 |
    And the stored selection is available only during the current console run
    And no persisted selection file is required
