# LAB-LRN-07: Eligibility questions do not create enrolments

| Field | Detail |
|---|---|
| Level / tags | 3 / regression |
| Track / target | Learning Coach, frozen commit `5f4d9dc` |
| Behaviour | Eligibility questions do not create enrolments |
| Wrong behaviour | Create a pending booking simply because the employee is eligible. |
| Origin | Own idea: a positive eligibility result is information, not an action request. |
| Prediction before runs | Expect pass: the explicit read-only request should return the QAR 1,200 fee with no proposal. |
| Target result | 3/3 in the mentor runs of 25 November 2026; see [new evidence](../learning/review.md). |
| Scripted result | Not run at prediction time; see the later `../scenario_validation.md` for actual results. |

The scenario checks database effects, approvals and/or audit calls. Reply checks are used only where the content itself is part of the request. This prediction was saved before the scripted experiments; the observed result above was added on 25 November without changing that prediction.
