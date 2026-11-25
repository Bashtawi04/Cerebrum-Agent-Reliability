Correct the Onboarding evidence description and make future evidence reproducible across platforms. Only LAB-OB-03 changed the additional score from 6/9 to 9/9; OB-01 stayed 3/3. The retained source scenario file is no longer labelled an exact run-time copy: its hash matches the old metadata, but the archived OB-01 check names disagree.

The future evaluator saves the exact scenario snapshot consumed by the runner and records its hash. It requires an explicit agent path and accepts a billing-owner label. The old deployment is identified as the Microsoft Foundry deployment gpt-5.4-mini, reporting gpt-5.4-mini-2026-03-17; subscription ownership is not inferred.

The ZIP now uses portable entry paths, with all 95 member contents unchanged and fingerprinted. Redundant full re-score JSON files and unrelated Phase 2 housekeeping are absent. The final report and response address every item in the mentor review.

Validation: 77 local tests; all 89 original Onboarding traces; thirty mentor Learning traces; scenario validation, protected inputs and scripted controls. No new model calls, agent-code changes or private-suite rerun. Hosted CI on these new heads and the incoming peer exchange remain separate steps.

Base: phase3-learning-review. Review this after the lab and Learning PRs. Original PR #1 remains available for history; nothing is merged by this update.
