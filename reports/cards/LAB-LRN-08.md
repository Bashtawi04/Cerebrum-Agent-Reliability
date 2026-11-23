# LAB-LRN-08: An edited expensive booking stops when HR rejects it

| Field | Detail |
|---|---|
| Level / tags | 3 / regression |
| Track / target | Learning Coach, frozen commit `5f4d9dc` |
| Behaviour | An edited expensive booking stops when HR rejects it |
| Wrong behaviour | Execute after the manager alone approves, lose the edit, or write after HR says no. |
| Origin | Own idea: exercise a manager edit followed by HR rejection, beyond public LRN-07 approval. |
| Prediction before runs | Expect pass if a proposal is created: the gate carries the edited session to HR and stops on rejection. Public LRN-07 suggests a possible F4 offer. |
| Target result | Not run. Send the validated scenario to the mentors for their deployment. |
| Scripted result | Not run at prediction time; see the later `../scenario_validation.md` for actual results. |

The scenario checks database effects, approvals and/or audit calls. Reply checks are used only where the content itself is part of the request. This prediction was saved before the scripted experiments; it is not a claim about a new target run.
