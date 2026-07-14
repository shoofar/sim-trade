# Sprint 0 Foundations QA Suite

## Purpose

Verify that Sprint 0 documents a clear MVP scope, BDD use cases, and visible examples.

## Preconditions

- Review the Sprint 0 foundations feature and related project docs in the Specifier worktree.
- Use the documentation as the visible interface.
- Do not use a project API.

## Scenario 1: Define the MVP scope

1. Open the Sprint 0 foundations specification.
2. Confirm the scope states that the application checks for available instrument data after startup.
3. Confirm the scope states that instruments come from the `DANE/<instrument>` directory structure.
4. Confirm the scope states that users can view available dates after choosing an instrument.
5. Confirm the scope states that instrument and date combinations are recorded.

## Scenario 2: Define visible examples

1. Open the Sprint 0 foundations specification.
2. Confirm the examples name a concrete instrument such as `MESM6`.
3. Confirm the examples include a concrete date such as `2026-05-01`.
4. Confirm the examples include a concrete timeframe such as `tick` or `1 min`.

## Scenario 3: Define the first BDD use cases

1. Open the Sprint 0 foundations specification.
2. Confirm the first use cases are written in Given, When, Then form.
3. Confirm each use case describes observable behavior.
4. Confirm each use case avoids implementation details.
