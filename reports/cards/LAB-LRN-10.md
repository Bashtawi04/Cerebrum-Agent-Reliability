# LAB-LRN-10: Book, cancel and rebook use separate action keys

| Field | Detail |
|---|---|
| Level / tags | 3 / regression |
| Track / target | Learning Coach, frozen commit `5f4d9dc` |
| Behaviour | Book, cancel and rebook use separate action keys |
| Wrong behaviour | Reuse the original booking key and return the cancelled booking as though it were new, or create duplicates. |
| Origin | Own idea: repeated legitimate actions must not be mistaken for retry duplicates. |
| Prediction before runs | Expect pass if the model follows all three turns: the executor includes a write counter in its key. A stale-state refusal remains possible. |
| Target result | 3/3 in the mentor runs of 25 November 2026; see [new evidence](../learning/review.md). |
| Scripted result | Not run at prediction time; see the later `../scenario_validation.md` for actual results. |

The scenario checks database effects, approvals and/or audit calls. Reply checks are used only where the content itself is part of the request. This prediction was saved before the scripted experiments; the observed result above was added on 25 November without changing that prediction.
