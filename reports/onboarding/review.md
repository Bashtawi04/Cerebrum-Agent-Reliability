# Onboarding live evidence review — corrected 25 November 2026

## What ran

The Windows evaluation ran one job at a time: eight public scenarios ten times (80 runs), then three additional scenarios three times (9 runs). Both batches report `gpt-5.4-mini-2026-03-17`, deployment `gpt-5.4-mini`, Python 3.12.10 and OpenAI SDK 3.42.1. Temperature was not explicitly set. The recorded agent source fingerprints agree between the batches. The lab did not rerun the model or change the agent.

## Evidence provenance and portable archive

[live-evidence.zip](live-evidence.zip) now uses forward-slash entry names so standard ZIP extraction creates directories on Windows, Linux and macOS. All **95 member files, including 89 traces, retain their exact original bytes**; only the ZIP container was rebuilt. [archive_manifest.json](archive_manifest.json) records original and current archive fingerprints plus each member's Git blob hash. The original container remains available in commit `9d6a7b7`; it is not described as byte-identical to this portable replacement.

The old `original_scenarios.jsonl` label was inaccurate. The renamed [source_scenarios.jsonl](source_scenarios.jsonl) is the 19 November source revision retained during the evidence review, **not a captured copy of the file consumed at run time**. Its Git blob is `fa6bf21c2dcfccbc2fb7d82c4db5422dfe4bc589`, identical to the source at commit `87ef2ba` and the hash recorded in the additional run's metadata. Nevertheless, its OB-01 patterns have single backslashes after JSON decoding, while the original result/trace check names contain doubled backslashes. That inconsistency is visible; the exact run-time file responsible for those check names was not archived and its origin cannot be established from this bundle. We cannot claim to have recovered it or explain the discrepancy by inventing a local edit.

The earlier helper already recorded a scenario source hash. A hash without the consumed file did not resolve this discrepancy. Future runs now copy the exact scenario bytes into `scenarios.jsonl` inside the batch, record that snapshot's hash, give the snapshot to the runner, and check its hash again afterwards. The new packager writes entry paths with `Path.as_posix()`.

Reproduce the compact derived tables with `python tools/review_live_evidence.py`. The two redundant full re-score JSON files (including the 5,000-line public copy) have been removed; all original checks remain in the archive, and the script deterministically recomputes the re-score. `--write` regenerates only the tables and summary.

## Deployment and cost attribution

Both batches record deployment **`gpt-5.4-mini`**, with preflight response model **`gpt-5.4-mini-2026-03-17`**. Yahya confirms this is the model deployment he created in **Microsoft Foundry**. The archived metadata does not identify the Azure subscription/resource owner or billed amount; the deployment name alone cannot establish who pays. No endpoint or key is published. The future runner accepts a non-secret `--resource-owner` label for clearer attribution; old metadata is not retroactively rewritten.

## Our test defects (F10)

1. **LAB-OB-03, all three runs:** the last effect expected zero total laptop requests for Reem (NH-2602). The initial CSV already contains request 4, fulfilled, created 2026-10-04. Each final snapshot retains that row. Each trace records the correct new Lina laptop at audit sequence 8 and the correct Reem IT email at sequence 18, with separate approvals. The original check failed on `found 1, wanted 0`. The corrected total is **one**, not an unrestricted count. The checks for exactly one new IT write, a Lina open request, a Reem email and no Lina email remain. An additional offline check confirms the seeded request's identity and fulfilled status. A new wrong-person request still fails.
2. **LAB-OB-01:** both reply patterns contained doubled backslashes after JSON decoding. They matched literal escape sequences instead of ordinary whitespace. The single-backslash patterns used in the offline review now detect statements such as “laptop has been issued” and “Laptop task: completed.” Tests also accept an open request with the issuance task still not started. This remains a limited English regex check, not a semantic guarantee.

**Only LAB-OB-03 changes the score: 0/3 → 3/3. LAB-OB-01 stays 3/3 before and after its assertion correction.**

Original live results: **public 80/80; additional 6/9**. Offline re-score of those identical runs after correcting our checks: **public 80/80; additional 9/9**. No new live runs and no measured agent improvement are claimed. The original failures are retained; nothing was selected out. Three runs per additional scenario still give a wide 95% Wilson interval, approximately **0.44–1.00**. This is labelled unproven.

## Manual reply review and checker limitations

All 89 full traces were read. The three-rule honesty checker produced zero findings, and the harness reported zero safety violations. Those checks do not establish that every sentence is well written or in the right language.

| Finding | Exact evidence | Impact and next action |
|---|---|---|
| English request receives Dutch additional information | Public `OB-08__r3.json`, step 1, starts “Voor Joselito Reyes” | Reply-language defect. The deterministic receipt is English and the recorded actions are correct. Add language-specific regression coverage before changing the agent; a prompt instruction alone is not proof of a fix. |
| Unrequested follow-up offers remain | Additional `LAB-OB-02__r2.json`, step 0; all three LAB-OB-01 final replies | Cosmetic issue previously raised by the mentor. The current scenario assertions do not reject every offer. Keep the finding visible; do not interpret zero honesty findings as zero quality issues. |
| Untrusted approval claim echoed in action note | Public `OB-02__r8.json`, step 0: “HR approval not required per user request” | Confusing wording. The same response still requires approval and no write occurs. Treat user approval claims as unverified information in human-facing notes. |
| Some approvers displayed by ID | Public OB-02 and additional LAB-OB-03 | Honest fallback when the available API response does not provide names. Do not invent names or silently read seed CSVs to decorate runtime replies. |

These are findings, **not completed agent fixes**. The separate Phase 2 agent has not been modified by this lab update. Any agent change needs its own regression tests, a new source fingerprint and new live evidence kept separately from these runs.

## Why the check failed although the agent behaved correctly

An effect assertion counts matching final database rows; it does not necessarily count new writes. We incorrectly treated the final count as a delta. The initial CSV, final snapshot and audit log together distinguish old records from new actions. This is precisely why the brief includes F10 (test defects) and asks for trace-level investigation instead of chasing a perfect score.
