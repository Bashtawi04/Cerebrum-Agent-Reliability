# LAB-LRN-02: Explain the retired course while completing the eligible booking

| Field | Detail |
|---|---|
| Level / tags | 3 / regression, multi_request |
| Track / target | Learning Coach, frozen commit `5f4d9dc` |
| Behaviour | Explain the retired course while completing the eligible booking |
| Wrong behaviour | Book LD-103 but silently omit the rejected LD-105 request. |
| Origin | CS-L2, recorded suite runs 1-6; reverses the order and explicitly asks for the refusal reason. |
| Prediction before runs | Expect F5: the code-written approval and final receipt may omit the policy refusal for LD-105. |
| Target result | 0/3 in the mentor runs of 25 November 2026; see [new evidence](../learning/review.md). |
| Scripted result | Not run at prediction time; see the later `../scenario_validation.md` for actual results. |

The scenario checks database effects, approvals and/or audit calls. Reply checks are used only where the content itself is part of the request. This prediction was saved before the scripted experiments; the observed result above was added on 25 November without changing that prediction.
