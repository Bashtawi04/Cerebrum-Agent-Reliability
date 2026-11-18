# Why three runs are not enough, in numbers

An agent that uses a language model gives different answers to the same request. So "it passed" is a statement about the
runs you happened to do, not about the agent.

**1. The chance of three perfect runs.** If a scenario's true pass rate is p, the chance of passing three runs in a row is p x p x p.

| true pass rate p | chance of 3/3 |
|---|---|
| 60% | 22% |
| 70% | 34% |
| 80% | 51% |
| 90% | 73% |
| 95% | 86% |

An agent that fails one request in five will still show "3/3" half the time.

**2. An interval is more honest than a ratio.** 3/3 and 30/30 are both "100%", but they mean different things. The Wilson interval
turns `passes` out of `runs` into a range that very probably contains the true pass rate. For 3/3 it is 0.44 to 1.00. For 10/10
it is 0.72 to 1.00. For 7/9 it is 0.45 to 0.94. When you write a pass rate in a report, write the interval too.

**3. How many perfect runs before you may say "at least 80%"?** 16. For "at least 90%": 35. This is why we report the label
`unproven` for a scenario that passed every run but has too few runs to rule out a weakness. (`runs_for_lower_bound` in `lab/stats.py`
computes these numbers.)

**4. pass^k and pass@k.** Both are estimated from n runs of which c passed.
* **pass^k** is the chance that k runs in a row ALL pass: C(c, k) / C(n, k). It goes down as k grows. Use it for anything a
  customer relies on every time. (The tau-bench paper used this idea to show that agents that look good on one run are often
  unreliable on eight.)
* **pass@k** is the chance that AT LEAST ONE of k runs passes: 1 - C(n - c, k) / C(n, k). It goes up as k grows. It is the right
  measure when you can simply try again and a single success is enough.

For an agent that writes to a system of record, quote pass^3, never pass@3.

**5. Clean runs.** Each run must start from the same state (the runner builds a fresh database and an empty state folder for
every run). Do not reuse an agent state folder between runs, and do not let one run's output be another's input.

**6. Read the failures.** A number tells you how often. Only a trace tells you why. Classify every failing run with
`docs/TAXONOMY.md` before you decide what to change, and rerun a failing scenario alone before you blame the agent: a rate limit
or a timeout looks exactly like a bug.
