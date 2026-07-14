# mutation-stamp: sha256=07c7faf5b9c9af8bd25472db4ef56c27a2d18db9b4787a967259e739ca297752
# acceptance-mutation-manifest-begin
# {"version":1,"tested_at":"2026-07-14T21:31:48Z","feature_name":"Console in-memory data table","feature_path":"acceptance\\features\\console_in_memory_data_table.feature","background_hash":"5ecf4db6a59f0d7b8e2496c753d3f1a80b97f5cadbf679213080ecb1088c65e3","implementation_hash":"unknown","scenarios":[]}
# acceptance-mutation-manifest-end

# Console in-memory data table 001
Feature: Console in-memory data table
  The console application stores loaded CSV records in memory for the current run.

  Background:
    Given the application is started from the project root
    And the local data directory "DANE" is available
    And the user has selected an available instrument, date, and timeframe

  # Console in-memory data table 001
  Scenario: Console in-memory data table 001 stores required fields for a loaded CSV
    Given the selected CSV file is comma-separated and contains 4 valid records
    When the user asks the console application to load the selected CSV
    Then the application stores 4 records in the in-memory data table
    And each stored record contains only fields:
      | field         |
      | ts_event      |
      | instrument_id |
      | side          |
      | price         |
      | size          |
      | sequence      |
      | symbol        |
      | timeframe     |
      | source        |
    And the console output reports that 4 records are stored in memory
    And the console output displays at most 3 records

  # Console in-memory data table 002
  Scenario: Console in-memory data table 002 supports the agreed maximum record count
    Given the selected CSV file is comma-separated and contains 20000 valid records
    When the user asks the console application to load the selected CSV
    Then the application stores 20000 records in the in-memory data table
    And the console output reports that 20000 records are stored in memory
    And the console output displays at most 3 records
    And the console application exits without a traceback

  # Console in-memory data table 003
  Scenario: Console in-memory data table 003 rejects files above the agreed maximum record count
    Given the selected CSV file is comma-separated and contains 20001 valid records
    When the user asks the console application to load the selected CSV
    Then the console output reports that the selected CSV exceeds the 20000 record limit
    And the application does not store a partial in-memory data table for the selected CSV
    And the console application exits without a traceback

  # Console in-memory data table 004
  Scenario: Console in-memory data table 004 reports an empty CSV without sample records
    Given the selected CSV file is comma-separated and contains no data records
    When the user asks the console application to load the selected CSV
    Then the application stores 0 records in the in-memory data table
    And the console output reports that 0 records are stored in memory
    And the console output does not display sample records
    And the console application exits without a traceback

  # Console in-memory data table 005
  Scenario: Console in-memory data table 005 is available only during the current run
    Given the selected CSV file is comma-separated and contains 4 valid records
    When the user asks the console application to load the selected CSV
    Then the application stores 4 records in the in-memory data table
    And the stored data table is available only during the current console run
    And no persisted data table file is required
