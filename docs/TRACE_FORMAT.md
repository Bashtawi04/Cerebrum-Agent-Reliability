# What the runner writes down (harness version 1.1)

Two kinds of files. The first you already know; the second is new.

## 1. The `--out` file (one per runner call)

A JSON list, one entry per scenario:

```json
{"id": "OB-07", "level": 3, "title": "...", "tags": ["regression"],
 "passes": 2, "runs": 3, "violations": ["write_before_approval"],
 "detail": [ {"id": "OB-07", "passed": true, "checks": [ {"name": "final_status", "ok": true, "detail": ""} ],
              "violations": [], "notes": [], "final_status": "done", "seconds": 14.2,
              "approval_requests": 1, "messages": ["..."], "trace": "OB-07__r1.json"} ]}
```

* `passes` and `runs` are counted over this call only. Several files can be merged by `lab/aggregate.py`.
* `violations` lists the kinds of safety violation seen in any run (`write_before_approval`, `write_after_reject`,
  `fabricated_approval`, `tried_write_without_approval`).
* `detail[].checks` has every check of the run, passed or failed. A failed check has `"ok": false`.
* `tags` is copied from the scenario if it has a `"tags"` list. `trace` is there only when you used `--trace-dir`.

## 2. The trace files (`--trace-dir DIR`: one file per run)

File name: `<scenario id>__r<run number>.json`. Content:

| Key | Meaning |
|---|---|
| `format` | 1 |
| `scenario`, `run`, `title`, `user`, `thread` | which scenario, which repeat, who was talking, the conversation id |
| `passed`, `final_status`, `protocol_error` | the verdict, the last status the agent returned, and a message if the agent broke the contract |
| `steps` | one entry per command the runner sent to the agent, in order (below) |
| `audit` | every call PeopleHub saw during the run: `seq`, `function`, `kind` (`read` or `write`), `args` (JSON text), `actor`, `approved_by`, `outcome` (`ok` or `error`), `error_code`, `result` |
| `write_tables` | `{"table name": [one object per row, with the column names as keys], ...}`: the final rows of every table the agent's writes can change |
| `checks`, `violations`, `notes` | as in the `--out` file |

A **step**:

| Key | Meaning |
|---|---|
| `i` | position, from 0 |
| `cmd` | `start`, `say` or `resume` |
| `args` | the arguments the runner passed (`--thread`, `--user`, `--message`, or `--decision`, `--by`, `--edit`) |
| `status`, `message`, `pending` | what the agent printed: `done`, `awaiting_approval` or `error`; the text for the user; the action waiting for a human |
| `seconds`, `stderr_tail` | how long it took; the last 300 characters the agent wrote to standard error |
| `audit_seqs` | the `seq` numbers of the audit rows written while this command ran. That is how you tell which calls belong to which step |
| `decision` | for a step that ended with `awaiting_approval`: what the runner then did, as `{"decision": "approve", "by": "E1008", "edit": null}` (`edit` holds the changes for `modify`; for `leave_pending` the object is only `{"decision": "leave_pending"}`); `null` for any other step |

Reading a trace in order is the quickest way to answer "why did this run fail": look at each step's `message`, then at the
audit rows its `audit_seqs` point to.

Traces contain the agent's replies and the fictional HR data. They are not secrets, but do not commit hundreds of them;
keep the few you quote in a report under `reports/evidence/`.
