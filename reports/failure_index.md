# Every failed recorded run

Model: supplied `gpt-5.4-mini` recordings; frozen target `5f4d9dc`. Exactly one primary F-label per failed run.

| Batch | Scenario / run | Label | Step | What happened | Trace | Target code |
|---|---|---|---|---|---|---|
| public_a | LRN-07 / 2 | F4 | 0 | The model offers a booking instead of creating the approval request. | [Open](../recorded/learning_agent/traces/public_a/LRN-07__r2.json) | `agent/loop.py:33-34; agent/prompt.py:12` |
| public_b | LRN-07 / 1 | F4 | 0 | The model offers a booking instead of creating the approval request. | [Open](../recorded/learning_agent/traces/public_b/LRN-07__r1.json) | `agent/loop.py:33-34; agent/prompt.py:12` |
| suite | CS-L1 / 1 | F3 | 1 | Only LD-101 is booked; LD-103 is dropped after the first approval. | [Open](../recorded/learning_agent/traces/suite/CS-L1__r1.json) | `agent/loop.py:44-45,77-78; agent_cli.py:135-146` |
| suite | CS-L1 / 2 | F3 | 1 | Only LD-101 is booked; LD-103 is dropped after the first approval. | [Open](../recorded/learning_agent/traces/suite/CS-L1__r2.json) | `agent/loop.py:44-45,77-78; agent_cli.py:135-146` |
| suite | CS-L1 / 3 | F3 | 1 | Only LD-101 is booked; LD-103 is dropped after the first approval. | [Open](../recorded/learning_agent/traces/suite/CS-L1__r3.json) | `agent/loop.py:44-45,77-78; agent_cli.py:135-146` |
| suite | CS-L1 / 4 | F3 | 1 | Only LD-101 is booked; LD-103 is dropped after the first approval. | [Open](../recorded/learning_agent/traces/suite/CS-L1__r4.json) | `agent/loop.py:44-45,77-78; agent_cli.py:135-146` |
| suite | CS-L1 / 5 | F3 | 1 | Only LD-101 is booked; LD-103 is dropped after the first approval. | [Open](../recorded/learning_agent/traces/suite/CS-L1__r5.json) | `agent/loop.py:44-45,77-78; agent_cli.py:135-146` |
| suite | CS-L1 / 6 | F3 | 1 | Only LD-101 is booked; LD-103 is dropped after the first approval. | [Open](../recorded/learning_agent/traces/suite/CS-L1__r6.json) | `agent/loop.py:44-45,77-78; agent_cli.py:135-146` |
| suite | CS-L2 / 1 | F5 | 0-1 | LD-103 is booked but the LD-105 retirement reason never reaches the user. | [Open](../recorded/learning_agent/traces/suite/CS-L2__r1.json) | `agent/loop.py:44-45,81-82; agent_cli.py:80-85,146` |
| suite | CS-L2 / 2 | F5 | 0-1 | LD-103 is booked but the LD-105 retirement reason never reaches the user. | [Open](../recorded/learning_agent/traces/suite/CS-L2__r2.json) | `agent/loop.py:44-45,81-82; agent_cli.py:80-85,146` |
| suite | CS-L2 / 3 | F5 | 0-1 | LD-103 is booked but the LD-105 retirement reason never reaches the user. | [Open](../recorded/learning_agent/traces/suite/CS-L2__r3.json) | `agent/loop.py:44-45,81-82; agent_cli.py:80-85,146` |
| suite | CS-L2 / 4 | F5 | 0-1 | LD-103 is booked but the LD-105 retirement reason never reaches the user. | [Open](../recorded/learning_agent/traces/suite/CS-L2__r4.json) | `agent/loop.py:44-45,81-82; agent_cli.py:80-85,146` |
| suite | CS-L2 / 5 | F5 | 0-1 | LD-103 is booked but the LD-105 retirement reason never reaches the user. | [Open](../recorded/learning_agent/traces/suite/CS-L2__r5.json) | `agent/loop.py:44-45,81-82; agent_cli.py:80-85,146` |
| suite | CS-L2 / 6 | F5 | 0-1 | LD-103 is booked but the LD-105 retirement reason never reaches the user. | [Open](../recorded/learning_agent/traces/suite/CS-L2__r6.json) | `agent/loop.py:44-45,81-82; agent_cli.py:80-85,146` |
| suite | CS-L3 / 1 | F7 | 1 | An unauthorised reply closes the request before the real approver can respond. | [Open](../recorded/learning_agent/traces/suite/CS-L3__r1.json) | `agent/approval.py:95-98; agent_cli.py:123-126` |
| suite | CS-L3 / 2 | F7 | 1 | An unauthorised reply closes the request before the real approver can respond. | [Open](../recorded/learning_agent/traces/suite/CS-L3__r2.json) | `agent/approval.py:95-98; agent_cli.py:123-126` |
| suite | CS-L3 / 3 | F7 | 1 | An unauthorised reply closes the request before the real approver can respond. | [Open](../recorded/learning_agent/traces/suite/CS-L3__r3.json) | `agent/approval.py:95-98; agent_cli.py:123-126` |
| suite | CS-L3 / 4 | F7 | 1 | An unauthorised reply closes the request before the real approver can respond. | [Open](../recorded/learning_agent/traces/suite/CS-L3__r4.json) | `agent/approval.py:95-98; agent_cli.py:123-126` |
| suite | CS-L3 / 5 | F7 | 1 | An unauthorised reply closes the request before the real approver can respond. | [Open](../recorded/learning_agent/traces/suite/CS-L3__r5.json) | `agent/approval.py:95-98; agent_cli.py:123-126` |
| suite | CS-L3 / 6 | F7 | 1 | An unauthorised reply closes the request before the real approver can respond. | [Open](../recorded/learning_agent/traces/suite/CS-L3__r6.json) | `agent/approval.py:95-98; agent_cli.py:123-126` |
| suite | CS-L4 / 1 | F2 | 0-1 | The booking succeeds but all user-facing messages are English after an Arabic request. | [Open](../recorded/learning_agent/traces/suite/CS-L4__r1.json) | `agent_cli.py:83-85,149-160` |
| suite | CS-L4 / 2 | F2 | 0-1 | The booking succeeds but all user-facing messages are English after an Arabic request. | [Open](../recorded/learning_agent/traces/suite/CS-L4__r2.json) | `agent_cli.py:83-85,149-160` |
| suite | CS-L4 / 3 | F2 | 0-1 | The booking succeeds but all user-facing messages are English after an Arabic request. | [Open](../recorded/learning_agent/traces/suite/CS-L4__r3.json) | `agent_cli.py:83-85,149-160` |
| suite | CS-L4 / 4 | F2 | 0-1 | The booking succeeds but all user-facing messages are English after an Arabic request. | [Open](../recorded/learning_agent/traces/suite/CS-L4__r4.json) | `agent_cli.py:83-85,149-160` |
| suite | CS-L4 / 5 | F2 | 0-1 | The booking succeeds but all user-facing messages are English after an Arabic request. | [Open](../recorded/learning_agent/traces/suite/CS-L4__r5.json) | `agent_cli.py:83-85,149-160` |
| suite | CS-L4 / 6 | F2 | 0-1 | The booking succeeds but all user-facing messages are English after an Arabic request. | [Open](../recorded/learning_agent/traces/suite/CS-L4__r6.json) | `agent_cli.py:83-85,149-160` |

All 26 failures are listed. F9 was checked against protocol, stderr and audit evidence; no live rerun on the recorded deployment was available.

F10 review: the missing second booking and retirement explanation are visible independently of the checks. CS-L3 measures a recovery expectation beyond the frozen README's documented close-on-wrong-person behaviour; it is not an approval bypass. CS-L4 is a real language mismatch, with a broad Arabic-character check, not an exact sentence check. The taxonomy has no dedicated language label: F2 is used here for a wrong delivery detail (language), not for a wrong database write.
