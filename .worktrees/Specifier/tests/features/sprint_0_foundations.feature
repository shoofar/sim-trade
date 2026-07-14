# Scenario 1: Sprint 0 foundations
Feature: Sprint 0 foundations

  Background:
    Given the project is in Sprint 0

  Scenario: Sprint 0 foundations defines MVP scope
    When the MVP scope is documented
    Then the scope states that the application checks for available instrument data after startup
    And the scope states that available instruments are discovered from the `DANE/<instrument>` directory structure
    And the scope states that the user can view available dates after selecting an instrument
    And the scope states that instrument and date combinations are recorded

  Scenario Outline: Sprint 0 foundations gives examples of visible data organization
    When the MVP scope is documented
    Then the scope references the instrument "<instrument>"
    And the scope references the date "<date>"
    And the scope references the timeframe "<timeframe>"

    Examples:
      | instrument | date       | timeframe |
      | MESM6      | 2026-05-01 | tick      |
      | MESM6      | 2026-05-01 | 1 min     |

  Scenario: Sprint 0 foundations defines the BDD use cases
    When the first use cases are documented in BDD form
    Then each use case uses Given, When, and Then
    And each use case describes observable behavior
    And each use case avoids implementation details
