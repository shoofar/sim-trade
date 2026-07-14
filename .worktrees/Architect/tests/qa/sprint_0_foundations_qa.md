# Sprint 0 Foundations QA Suite

## Purpose

Verify that Sprint 0 documents a visible MVP scope, concrete DANE examples, and BDD use cases only.

## Preconditions

- Review the Sprint 0 foundations feature and the project `DANE/` directory.
- Use the documentation as the visible interface.
- Do not inspect internal schemas, module boundaries, or hidden implementation details.

## Scenario 1: Confirm the MVP scope

1. Open the Sprint 0 foundations specification.
2. Confirm it describes only user-visible behavior.
3. Confirm it states that instruments are discovered from `DANE/<instrument>`.
4. Confirm it states that users can view available dates after choosing an instrument.
5. Confirm it states that users can view available timeframes after choosing an instrument date.
6. Confirm it avoids CSV schema detail, data model detail, and module boundary detail.

## Scenario 2: Confirm the visible examples

1. Open the Sprint 0 foundations specification.
2. Confirm it names the instrument `MESM`.
3. Confirm it names the date `2026-05-01`.
4. Confirm it names the timeframe `trades`.

## Scenario 3: Confirm the BDD use cases

1. Open the Sprint 0 foundations specification.
2. Confirm the first use cases are written in Given, When, Then form.
3. Confirm each use case describes observable behavior.
4. Confirm each use case avoids implementation details.
