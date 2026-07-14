# Communication Pipeline

## Inbox model

- Every agent has an inbox under `agent_context/roles/<role>/inbox/`.
- A handoff to another agent is written as a file inside that agent's inbox.
- The filename must use the timestamp format `YYYYMMDD-HHMMSS.mmm`.
- The handoff file should contain the message payload and the target role.

## Notification

- After writing the handoff file, notify the target role using the same style of role-to-role delivery used in the earlier SwarmForge, such as `send_to_role`.
- The notification only states that a new message exists.
- The notification does not require master approval.
- Do not create duplicate inbox messages for the same handoff.
- When using `send_to_role ... /file`, prefer a source file outside the target role inbox, such as `agent_context/messages/`; the send script copies that file into the target inbox.
- If a handoff file is already in the target role inbox, `send_to_role ... /file` must only notify the target role about that existing file and must not copy it again under a new timestamp.

## Processing rule

- When an agent is notified about a new message, it does not interrupt the task it is currently executing.
- The agent finishes the current task first.
- After finishing the current task, the agent moves the oldest message in its `inbox/` to `agent_context/roles/<role>/working/`.
- The agent processes the message from `agent_context/roles/<role>/working/`.

## Completion rule

- When an agent finishes processing a message from `agent_context/roles/<role>/working/`, it moves that message to `agent_context/roles/<role>/done/`.
- Messages in `done/` are retained as processed history.

## Downstream notification

- If processing a message requires informing another role, the agent notifies that role directly.
- Those role-to-role notifications do not require master approval.
