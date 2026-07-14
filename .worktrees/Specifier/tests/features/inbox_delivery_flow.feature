# mutation-stamp: sha256=77daeef6fb96f4cec830baaf1edcba806331cbb89cc85001272f237aabdeff04
# acceptance-mutation-manifest-begin
# {"version":1,"tested_at":"2026-07-13T18:20:51Z","feature_name":"Inbox delivery flow","feature_path":"F:\\Python\\Swarm-Forge-2.0\\projects\\sim-server\\.worktrees\\Specifier\\tests\\features\\inbox_delivery_flow.feature","background_hash":"d1347e00d57ffaa56e941634487b1482973da35c91733dbab76e7dfa5f5c8e43","implementation_hash":"unknown","scenarios":[]}
# acceptance-mutation-manifest-end

# Scenario 1: Inbox delivery flow
Feature: Inbox delivery flow

  Background:
    Given a target role inbox exists
    And the target role has a done folder for processed messages

  Scenario: Inbox delivery flow delivers a message to the target inbox
    When a delivery message is sent to the target role
    Then the target role inbox contains the delivered message
    And the delivered message is addressed to the target role

  Scenario: Inbox delivery flow processes the oldest pending message first
    Given the target role inbox contains two pending messages in timestamp order
    When the target role starts processing its inbox
    Then the oldest pending message is processed first
    And the newer pending message remains pending until the older message is completed

  Scenario: Inbox delivery flow archives a processed message in done
    Given the target role inbox contains one pending message
    When the target role completes processing that message
    Then the message is moved from the inbox to the done folder
    And the done folder retains the processed message as history
