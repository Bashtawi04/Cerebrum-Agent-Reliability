# Response to Phase 3 findings on the Onboarding agent

**Status: awaiting the Phase 3 findings that the mentors will pass on.**

No Phase 3 incoming review is present in the supplied material. The Phase 2 reviews were a separate revision cycle; they are not presented as a completed Phase 3 peer review.

For each incoming finding, record the exact scenario and trace, agree or explain disagreement, add a regression case in `scenarios/lab_onboarding.jsonl`, and show the failing result before the fix and passing result after it. If model runs are available, use the same named model and run count, with Wilson intervals. Changes belong in the Onboarding repository; the reliability lab keeps its scenarios and evidence.

One existing Phase 2 limitation remains relevant: generated extra prose can overstate task completion even when the database receipt says only that an IT request is open. It is documented in the Phase 2 report. The current LAB-OB-01 runs did not reproduce physical-issuance overclaims. The reply patterns required an escaping correction before re-scoring. This limited result does not establish a general fix; the lab's basic any-write honesty rule would not necessarily catch such a claim.

## Our own review, 22 November

The test corrections and reply-quality findings in [onboarding/review.md](onboarding/review.md) are our own analysis, not an incoming teammate review. No agent code was changed. Language, unwanted offers and untrusted approval-note wording remain open; preserve this batch as evidence for future regression work.
