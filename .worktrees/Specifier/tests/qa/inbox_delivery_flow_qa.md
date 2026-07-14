# Inbox Delivery Flow QA Suite

## Purpose

Verify that role-to-role delivery creates inbox entries, preserves oldest-first processing, and moves processed messages to `done`.

## Preconditions

- Use the canonical send script in `scripts\send_to_role_psmux_separate_windows_clean.cmd`.
- Use a visible target role inbox under `agent_context\roles\<role>\inbox\`.
- Use the matching processed-message folder under `agent_context\roles\<role>\inbox\done\`.

## Scenario 1: Deliver a message to a role inbox

1. Choose a target role such as `Specifier`.
2. Send one message to that role using the canonical send script.
3. Observe a new message file appear in the target inbox.
4. Confirm the file content identifies the intended target role.

## Scenario 2: Process the oldest pending message first

1. Send two messages to the same target role in chronological order.
2. Start the target role through its normal user-visible runner.
3. Observe the oldest message leave `inbox` before the newer one.
4. Confirm the newer message remains pending until the older one is completed.

## Scenario 3: Archive a processed message in done

1. Complete processing of the selected message through the normal role UI flow.
2. Observe the processed message move from `inbox` to `inbox\done`.
3. Confirm the message remains available in `done` as processed history.
