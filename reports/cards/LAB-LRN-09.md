# LAB-LRN-09: Two temporary failures end without a false booking receipt

| Field | Detail |
|---|---|
| Level / tags | 3 / regression |
| Track / target | Learning Coach, frozen commit `5f4d9dc` |
| Behaviour | Two temporary failures end without a false booking receipt |
| Wrong behaviour | Keep retrying until a third write succeeds, or report success after both writes fail. |
| Origin | Own idea: extend public LRN-08 beyond one recoverable fault to the retry limit. |
| Prediction before runs | Expect pass: executor retries once and reports the second failure, with no successful write. |
| Target result | 3/3 in the mentor runs of 25 November 2026; see [new evidence](../learning/review.md). |
| Scripted result | Not run at prediction time; see the later `../scenario_validation.md` for actual results. |

The scenario checks database effects, approvals and/or audit calls. Reply checks are used only where the content itself is part of the request. This prediction was saved before the scripted experiments; the observed result above was added on 25 November without changing that prediction.
