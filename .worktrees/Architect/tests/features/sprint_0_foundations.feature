# Scenario 1: Sprint 0 foundations
Feature: Sprint 0 foundations

  Background:
    Given the project is in Sprint 0

  Scenario: Sprint 0 foundations defines the visible MVP scope
    When the MVP scope is documented
    Then the scope describes only user-visible behavior
    And the scope states that available instruments are discovered from the `DANE/<instrument>` directory structure
    And the scope states that the user can view available dates after selecting an instrument
    And the scope states that the user can view available timeframes after selecting an instrument date
    And the scope avoids CSV schema detail
    And the scope avoids data model detail
    And the scope avoids module and layer boundaries

  Scenario Outline: Sprint 0 foundations gives concrete DANE examples
    When the MVP scope is documented
    Then the scope references the instrument "<instrument>"
    And the scope references the date "<date>"
    And the scope references the timeframe "<timeframe>"

    Examples:
      | instrument | date       | timeframe |
      | MESM       | 2026-05-01 | trades    |

  Scenario: Sprint 0 foundations defines the BDD use cases
    When the first use cases are documented in BDD form
    Then each use case uses Given, When, and Then
    And each use case describes observable behavior
    And each use case avoids implementation details
