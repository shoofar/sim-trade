# mutation-stamp: sha256=6d2904c5816242f90a571fbd9369ed445d712ccfa92831733a444eff3792b3d3
# acceptance-mutation-manifest-begin
# {"version":1,"tested_at":"2026-07-14T13:05:11Z","feature_name":"Console instrument discovery","feature_path":"acceptance\\features\\console_instrument_discovery.feature","background_hash":"0bf9263c524731c2596dd7d579746452526d1204c6af6a8612c5a0a2814d3ec8","implementation_hash":"unknown","scenarios":[]}
# acceptance-mutation-manifest-end

# Console instrument discovery 001
Feature: Console instrument discovery
  The console application reports which instruments are available in local data storage.

  Background:
    Given the application is started from the project root

  # Console instrument discovery 001
  Scenario: Console instrument discovery 001 lists direct instrument directories
    Given the local data directory "DANE" contains instrument directories:
      | instrument |
      | MESM6      |
      | NQMM6      |
    When the user runs the console application
    Then the console output lists the available instruments:
      | instrument |
      | MESM6      |
      | NQMM6      |
    And the console output does not list timeframe directories
    And the console output does not show CSV records

  # Console instrument discovery 002
  Scenario: Console instrument discovery 002 ignores non-directory entries
    Given the local data directory "DANE" contains instrument directories:
      | instrument |
      | MESM6      |
    And the local data directory "DANE" contains a file named "README.txt"
    When the user runs the console application
    Then the console output lists the available instruments:
      | instrument |
      | MESM6      |
    And the console output does not list "README.txt" as an instrument

  # Console instrument discovery 003
  Scenario: Console instrument discovery 003 reports missing data directory
    Given the local data directory "DANE" does not exist
    When the user runs the console application
    Then the console output reports that no data directory is available
    And the console application exits without a traceback
