# Three-part review

The original PR #1 and `phase3-reliability` branch remain available as the historical submission, including prediction commit `50bf3f7`. No force push or merge is needed to review the correction.

| Review | Branch | Base | Scope |
|---|---|---|---|
| 1 | `phase3-lab-review` | `main` | Statistics edge cases, null-message handling, protected-input checks, honesty controls and CI |
| 2 | `phase3-learning-review` | `phase3-lab-review` | Ten scenarios, original predictions, scripted controls, new mentor traces and Learning findings |
| 3 | `phase3-onboarding-review` | `phase3-learning-review` | Own-agent evidence, provenance corrections, portable archives, explicit evaluation helper and final delivery report |

Each branch's `python tools/reproduce.py` validates the contents of that branch. Review in this order. The final branch includes all three. Phase 2 housekeeping is absent from all three replacement branches; it remains only in the historical submission.

All three branches are published, and hosted CI passed on their current heads: [lab](https://github.com/Bashtawi04/Cerebrum-Agent-Reliability/actions/runs/45815126637), [Learning](https://github.com/Bashtawi04/Cerebrum-Agent-Reliability/actions/runs/45815126898), and [Onboarding](https://github.com/Bashtawi04/Cerebrum-Agent-Reliability/actions/runs/45815126694). The replacement PRs have not yet been created. Compare links: [main <- lab](https://github.com/Bashtawi04/Cerebrum-Agent-Reliability/compare/main...phase3-lab-review?expand=1), [lab <- Learning](https://github.com/Bashtawi04/Cerebrum-Agent-Reliability/compare/phase3-lab-review...phase3-learning-review?expand=1), and [Learning <- Onboarding](https://github.com/Bashtawi04/Cerebrum-Agent-Reliability/compare/phase3-learning-review...phase3-onboarding-review?expand=1). Do not merge the old and replacement PRs together. No branch is marked accepted by the mentor.
