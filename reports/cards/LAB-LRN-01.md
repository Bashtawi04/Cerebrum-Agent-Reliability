# LAB-LRN-01: Both course requests survive the first approval

| Field | Detail |
|---|---|
| Level / tags | 3 / regression, multi_request |
| Track / target | Learning Coach, frozen commit `5f4d9dc` |
| Behaviour | Both course requests survive the first approval |
| Wrong behaviour | Book only the first course and forget the second. |
| Origin | CS-L1, recorded suite runs 1-6; reverses the course order. |
| Prediction before runs | Expect F3: the frozen CLI returns done after its first approved write and never resumes the original multi-course request. |
| Target result | Not run. Send the validated scenario to the mentors for their deployment. |
| Scripted result | Not run at prediction time; see the later `../scenario_validation.md` for actual results. |

The scenario checks database effects, approvals and/or audit calls. Reply checks are used only where the content itself is part of the request. This prediction was saved before the scripted experiments; it is not a claim about a new target run.

## Later scripted experiment

Correct fixture: **3/3**, Wilson 95% interval **0.44–1.00**, unproven. `drops_second` variant: **0/3**, interval **0.00–0.56**. No model was used. All three traces were inspected: the bad variant writes only LD-103 and never proposes LD-101.
