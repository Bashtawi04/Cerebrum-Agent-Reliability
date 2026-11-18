# Scenario card: <ID>

One card per scenario you add to `scenarios/lab_<track>.jsonl`. Keep it short.

| | |
|---|---|
| **ID, level, tag** | e.g. LAB-ONB-03, level 3, regression |
| **Track and target** | which track's agent this is written for |
| **Behaviour it checks** | one sentence, in words a user would use |
| **Wrong behaviour it should catch** | what a bad agent does that makes this fail |
| **Where the idea came from** | a failure you saw (run id or trace), a review finding, or "my own idea" |
| **Passes on** | which agent(s) you ran it on, how many runs, how many passed (use the interval from `lab.aggregate`) |
| **Fails on** | same, for any agent where it fails; say whether you read the trace and what caused it (taxonomy label) |
| **How I tried to break it** | what you changed in an agent to make it do the wrong thing, and whether the scenario then failed |

If the scenario fails on an agent, state your **prediction before you run it** ("I expect this to fail on the target because it
only ever proposes one action per request") and then the result. Predictions you got wrong are worth keeping: they show what
you learned.
