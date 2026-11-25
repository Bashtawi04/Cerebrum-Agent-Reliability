# LAB-LRN-03: A booking and a saved draft both complete

| Field | Detail |
|---|---|
| Level / tags | 3 / capability, multi_request |
| Track / target | Learning Coach, frozen commit `5f4d9dc` |
| Behaviour | A booking and a saved draft both complete |
| Wrong behaviour | Save only the plan or book only the course; unnecessarily ask for plan approval. |
| Origin | Own idea: combine the low-risk plan write with a protected booking, after observing CS-L1. |
| Prediction before runs | Expect order-dependent F3 failures if the model proposes the booking before saving the draft; a same-batch low-risk write may succeed. |
| Target result | 2/3 in the mentor runs of 25 November 2026; see [new evidence](../learning/review.md). |
| Scripted result | Not run at prediction time; see the later `../scenario_validation.md` for actual results. |

The scenario checks database effects, approvals and/or audit calls. Reply checks are used only where the content itself is part of the request. This prediction was saved before the scripted experiments; the observed result above was added on 25 November without changing that prediction.
