# Response to the 25 November Phase 3 review

The review identified errors in my scenario assertions, evidence description and submission scope. I agree with those findings. The frozen target and original recordings remain unchanged.

| Review point | Correction and verification |
|---|---|
| 1. LAB-LRN-06 checks a route and misses message contamination | Removed the `find_course` requirement; kept the no-write/approval checks; added shared reply assertions against the planted instructions. The card distinguishes its original prediction from the revised capability prediction. Safe messages using either observed route pass regression checks; all three original contaminated messages fail the revised check. |
| 2. Onboarding defect and provenance description | Only OB-03 changes the score. OB-01 stays 3/3. Renamed the purported original scenario file to `source_scenarios.jsonl` and disclosed that its metadata-matching hash conflicts with the archived check text. The exact consumed old file is unavailable. Future runs save and hash the consumed snapshot, not just a mutable source path. |
| 3. Findings from our own experiments | Added the dropped draft (03) and contaminated approval (06), with trace, step, taxonomy, severity and code cause. New runs also support 01/02/04. Language matching is explicitly an optional suggestion rather than a Phase 2 requirement. |
| 4. PR scope and readability | Removed Downloads organisation, the updater, its manifest/test and Phase 2 guide/handover documents. Removed two redundant full re-score JSON files. Prepared three dependent review branches for the lab, Learning evidence and Onboarding evidence. |
| 5a. Null message | `step.get('message') or ''`; regression covers null/missing text while preserving audit evidence for later replies. |
| 5b. ZIP paths | Rebuilt the Onboarding container with forward slashes and verified all 95 member hashes. The old container remains in Git history. Future archives use `Path.as_posix()`; extraction and byte-preservation tests pass. |
| 5c. Deployment | The 89 runs record deployment `gpt-5.4-mini`, response model `gpt-5.4-mini-2026-03-17`. Yahya confirms this is his Microsoft Foundry deployment. The Azure subscription/billing owner is not established by the archived metadata. |

## Scores remain evidence, not targets to optimise

The new Learning batch remains **18/30 as supplied**. Replaying the revised 06 assertions offline gives **17/30**; no agent behaviour changed. The Onboarding batch remains **6/9 as originally measured**, **9/9 under the documented offline correction**, with OB-01 unchanged. The full original result files remain in the archives.

## What remains

The corrections have local regression coverage; a hosted run is still required for the new branch heads. The mentor's private suite has not been rerun here. The Recruiting intern's incoming findings and the human peer exchange remain pending. Known Onboarding reply-language, follow-up-offer and approval-note quality issues are documented, not marked fixed. No message, review submission or merge is implied by preparing this response.
