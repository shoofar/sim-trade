# mutation-stamp: sha256=abd1955483ebf17a377d6aeb9543c2c4d77bd2aaff48766e42e5206f21fa8183
# acceptance-mutation-manifest-begin
# {"version":1,"tested_at":"2026-07-14T20:39:39Z","feature_name":"Console instrument description","feature_path":"acceptance\\features\\console_instrument_description.feature","background_hash":"658e594fc65b379e212f89b69fa80eeb1a27aa7f416dc26f80d2ef286a6cee33","implementation_hash":"unknown","scenarios":[]}
# acceptance-mutation-manifest-end

# Console instrument description 001
Feature: Console instrument description
  The console application shows initial descriptive information for the selected instrument.

  Background:
    Given the application is started from the project root
    And the local data directory "DANE" is available
    And available instruments have been discovered from local directories

  # Console instrument description 001
  Scenario: Console instrument description 001 shows configured instrument details
    Given instrument "MESM6" has an initial description:
      | instrument | kind    | description             |
      | MESM6      | Futures | Micro E-mini S&P 500    |
    When the user runs the console application
    And the user selects instrument "MESM6"
    Then the console output shows the instrument name "MESM6"
    And the console output shows the instrument kind "Futures"
    And the console output shows the instrument description "Micro E-mini S&P 500"
    And the console output does not show CSV records

  # Console instrument description 002
  Scenario: Console instrument description 002 shows the default description when text is missing
    Given instrument "MESM6" has an initial description:
      | instrument | kind    | description              |
      | MESM6      | Futures | pusty - do uzupelnienia  |
    When the user runs the console application
    And the user selects instrument "MESM6"
    Then the console output shows the instrument name "MESM6"
    And the console output shows the instrument kind "Futures"
    And the console output shows the instrument description "pusty - do uzupelnienia"

  # Console instrument description 003
  Scenario: Console instrument description 003 uses default fields for a discovered instrument without configured details
    Given instrument "NQMM6" is discovered under the local data directory
    And instrument "NQMM6" has no configured initial description
    When the user runs the console application
    And the user selects instrument "NQMM6"
    Then the console output shows the instrument name "NQMM6"
    And the console output shows the instrument kind "pusty - do uzupelnienia"
    And the console output shows the instrument description "pusty - do uzupelnienia"
    And the console application exits without a traceback

  # Console instrument description 004
  Scenario: Console instrument description 004 does not allow editing descriptions in this slice
    Given instrument "MESM6" has an initial description:
      | instrument | kind    | description          |
      | MESM6      | Futures | Configured text      |
    When the user runs the console application
    And the user selects instrument "MESM6"
    Then the console output shows the initial description fields for "MESM6"
    And the console output does not offer a description editing workflow
