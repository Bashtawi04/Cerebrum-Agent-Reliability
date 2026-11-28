# Decision log

| Date | Decision | Reason |
|---|---|---|
| 2026-11-18 | Use the supplied recordings as the real-model measurement. | No model configuration is available here; old Phase 2 scores are not a substitute. |
| 2026-11-18 | Keep frozen inputs byte-identical and verify their Git blob hashes. | Findings must refer to the exact target the mentors supplied. |
| 2026-11-18 | Follow the specified sentence rules; document their blind spots. | Consistency with supplied/hidden tests matters; three rules are not a universal truth checker. |
| 2026-11-18 | Store predictions in a separate commit before running the new scenarios. | Avoid rewriting expectations after seeing results. |
| 2026-11-18 | Validate two scenarios with good and deliberately broken fixtures. | Demonstrate that their checks discriminate intended behaviour without buying model calls. |
| 2026-11-18 | Use F2 for CS-L4 with an explicit language qualification. | The fixed taxonomy has no language-specific category; the database action is correct. |
| 2026-11-18 | Treat CS-L3 as a recovery expectation, not an approval-security defect. | The frozen README documents closing the request and the traces show no unauthorised write. |
| 2026-11-18 | Archive known Phase 2 downloads with an undo manifest. | Reduce clutter without deleting evidence or disturbing the active repository and environment. |
| 2026-11-18 | Keep Phase 3 in a new local repository with a runnable main branch. | The brief requires separation and asks the mentors to confirm the remote destination. |

- 19 November: Audit added three own-agent cases and a separate live evaluation wrapper. Predictions precede execution. Source identifiers use the same Git blob SHA-1 format as the protected-input manifest; these identify revisions, not credentials. Failed runs remain evidence and are not hidden by the supplied harness returning exit code zero. No original runner, validator, target or supplied test was changed.

- 22 November: preserve the exact uploaded archive and original scenarios; re-score only documented faulty expectations offline. Do not call this a fresh live run or agent improvement. Keep wrong-language, offer and approval-note findings open.

- 23 November: record the mentor-approved GitHub destination and the exact successful hosted revision. Upgrade checkout/setup-python to their documented v7 releases to remove the old Node runtime warnings; verify the new hosted run separately. Preserve raw results, predictions, protected inputs and historical logs.

## 25 November 2026

- Done: analysed the returned thirty target traces, corrected LAB-LRN-06 and Onboarding provenance, fixed null-message handling, normalised archive paths and removed unrelated Phase 2 housekeeping.
- Next: publish the separated review branches, check their hosted CI, and complete the peer exchange when incoming findings arrive.
- Correction to 22 November wording: only OB-03 changed scores. The retained scenario source was not a captured run-time file. The portable ZIP preserves member bytes, not the original container bytes. No agent improvement or fresh model run is claimed.
