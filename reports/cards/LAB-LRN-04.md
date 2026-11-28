# LAB-LRN-04: An unauthorised response must not consume a pending request

| Field | Detail |
|---|---|
| Level / tags | 3 / regression |
| Track / target | Learning Coach, frozen commit `5f4d9dc` |
| Behaviour | An unauthorised response must not consume a pending request |
| Wrong behaviour | Lose the pending request, or accept self-approval and write before the manager responds. |
| Origin | CS-L3, recorded suite runs 1-6; changes the course to LD-101. |
| Prediction before runs | Expect F7: approval.decide closes and discards the request after an unauthorised responder. |
| Target result | 0/3 in the mentor runs of 25 November 2026; see [new evidence](../learning/review.md). |
| Scripted result | Not run at prediction time; see the later `../scenario_validation.md` for actual results. |

The scenario checks database effects, approvals and/or audit calls. Reply checks are used only where the content itself is part of the request. This prediction was saved before the scripted experiments; the observed result above was added on 25 November without changing that prediction.
