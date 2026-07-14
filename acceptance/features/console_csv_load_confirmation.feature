# mutation-stamp: sha256=40389c05b55df3f0eafed83f6c9fb9fd541adcdbfd47fba6f62b5670440ef9ab
# acceptance-mutation-manifest-begin
# {"version":1,"tested_at":"2026-07-14T21:04:11Z","feature_name":"Console CSV load confirmation","feature_path":"acceptance\\features\\console_csv_load_confirmation.feature","background_hash":"5ecf4db6a59f0d7b8e2496c753d3f1a80b97f5cadbf679213080ecb1088c65e3","implementation_hash":"unknown","scenarios":[]}
# acceptance-mutation-manifest-end

# Console CSV load confirmation 001
Feature: Console CSV load confirmation
  The console application confirms loading a selected CSV by showing up to three required-field records.

  Background:
    Given the application is started from the project root
    And the local data directory "DANE" is available
    And the user has selected an available instrument, date, and timeframe

  # Console CSV load confirmation 001
  Scenario: Console CSV load confirmation 001 shows up to three RAW-TICK records with required fields
    Given the selected CSV file is comma-separated and contains records:
      | ts_event                       | instrument_id | side | price          | size | sequence  | symbol |
      | 2026-05-01T00:00:00.035938849Z | 42005163      | B    | 7253.000000000 | 25   | 374608942 | MESM6  |
      | 2026-05-01T00:00:00.035938849Z | 42005163      | B    | 7253.250000000 | 2    | 374608943 | MESM6  |
      | 2026-05-01T00:00:00.037082405Z | 42005163      | A    | 7253.000000000 | 1    | 374609053 | MESM6  |
      | 2026-05-01T00:00:00.037109517Z | 42005163      | A    | 7253.000000000 | 2    | 374609054 | MESM6  |
    And the selected timeframe is "tick"
    And the selected source is "RAW-TICK"
    When the user asks the console application to load the selected CSV
    Then the console output confirms the CSV file is loaded
    And the console output displays exactly 3 records
    And each displayed record includes fields:
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
    And each displayed record shows timeframe "tick"
    And each displayed record shows source "RAW-TICK"

  # Console CSV load confirmation 002
  Scenario: Console CSV load confirmation 002 shows all records when fewer than three are loaded
    Given the selected CSV file is comma-separated and contains records:
      | ts_event                       | instrument_id | side | price          | size | sequence  | symbol |
      | 2026-05-01T00:00:00.035938849Z | 42005163      | B    | 7253.000000000 | 25   | 374608942 | MESM6  |
      | 2026-05-01T00:00:00.037082405Z | 42005163      | A    | 7253.000000000 | 1    | 374609053 | MESM6  |
    And the selected timeframe is "tick"
    And the selected source is "RAW-TICK"
    When the user asks the console application to load the selected CSV
    Then the console output confirms the CSV file is loaded
    And the console output displays exactly 2 records

  # Console CSV load confirmation 003
  Scenario: Console CSV load confirmation 003 rejects a CSV missing a required column
    Given the selected CSV file is comma-separated and lacks required column "sequence"
    When the user asks the console application to load the selected CSV
    Then the console output reports missing required column "sequence"
    And the console output does not display partial records
    And the console application exits without a traceback

  # Console CSV load confirmation 004
  Scenario: Console CSV load confirmation 004 does not expose non-required CSV columns as model fields
    Given the selected CSV file is comma-separated and contains required columns
    And the selected CSV file also contains non-required columns:
      | column       |
      | publisher_id |
      | flags        |
      | ts_recv      |
    When the user asks the console application to load the selected CSV
    Then the console output displays loaded records with only the required model fields
    And the console output does not display "publisher_id" as a model field
    And the console output does not display "flags" as a model field
    And the console output does not display "ts_recv" as a model field

  # Console CSV load confirmation 005
  Scenario: Console CSV load confirmation 005 shows OHLC source for a selected OHLC data category
    Given the selected CSV file is comma-separated and contains required columns
    And the selected timeframe is "1s"
    And the selected source is "OHLC"
    When the user asks the console application to load the selected CSV
    Then each displayed record shows timeframe "1s"
    And each displayed record shows source "OHLC"
