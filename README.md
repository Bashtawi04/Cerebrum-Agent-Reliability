# Agent Reliability Lab — core review

**Yahya AlBashtawi · Cerebrum · Phase 3**

This first review contains the statistics/checker corrections, protected-input checks, honesty controls and offline CI. It is based on the runnable `main` foundation. The Learning and Onboarding evidence are separate dependent reviews; see [the branch plan](reports/review_branches.md).

## Reproduce

Python 3.10+ and Git; standard library only. From this directory:

```powershell
python -X utf8 tools/reproduce.py
```

On Linux/macOS:

```bash
python3 -X utf8 tools/reproduce.py
```

This branch runs 59 tests, checks 232 protected input hashes, reproduces the two supplied tables and public A→B gate, and verifies the honesty controls. It makes no model calls.

## Corrections

- Null or missing message text is treated as empty, while audit evidence still carries forward to later replies.
- Statistics functions reject invalid `k` arguments consistently.
- Extra tests cover unreferenced writes, whole-word matching, required claim forms and invalid statistics inputs.
- CI checks Python 3.10 and 3.12. A new hosted run is needed after this branch is published.

The 47 supplied tests, frozen target, harness and recordings remain unchanged. Zero checker findings is limited to its three rules; [the honesty review](reports/honesty_review.md) explains the blind spots. The public A→B gate detects no regression under its rules; it does not certify the agent or the separate colleague suite.

This branch contains no Phase 2 housekeeping, live evaluation or file-moving tools. New Learning traces and findings are in `phase3-learning-review`; own-agent evidence and final status are in `phase3-onboarding-review`. Neither has been merged or accepted by the mentor merely by being prepared.
