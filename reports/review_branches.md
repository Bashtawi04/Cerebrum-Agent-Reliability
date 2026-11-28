# Three-part review

The original PR #1 and `phase3-reliability` branch remain available as the historical submission, including prediction commit `50bf3f7`. No force push or merge is needed to review the correction.

| Review | Branch | Base | Scope |
|---|---|---|---|
| 1 | `phase3-lab-review` | `main` | Statistics edge cases, null-message handling, protected-input checks, honesty controls and CI |
| 2 | `phase3-learning-review` | `phase3-lab-review` | Ten scenarios, original predictions, scripted controls, new mentor traces and Learning findings |
| 3 | `phase3-onboarding-review` | `phase3-learning-review` | Own-agent evidence, provenance corrections, portable archives, explicit evaluation helper and final delivery report |

Each branch's `python tools/reproduce.py` validates the contents of that branch. Review in this order. The final branch includes all three. Phase 2 housekeeping is absent from all three replacement branches; it remains only in the historical submission.

These branches are prepared locally. Publishing, hosted CI and PR creation must be verified separately. Once all three replacement PRs exist, PR #1 can be closed as superseded with links, preserving the mentor's original review context. Do not merge the old and replacement PRs together. No branch is marked accepted by the mentor.
