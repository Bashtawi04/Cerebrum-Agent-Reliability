# Phase 3: the reliability lab (Onboarding Agent, Agent Bank ID 32)

**Start with `03_Phase3_Brief_Onboarding_Agent.pdf`.** It explains the task, the levels and how it will be judged.

1. `docs/NO_AZURE.md` (you do not need a model key for this task), then `docs/STATS_NOTES.md` and `docs/TAXONOMY.md`: a few minutes each.
2. `harness/README.md`: the test runner. Same contract as Phase 2, plus `--agent-dir` and `--trace-dir`.
3. `lab/` and `tests/`: your code and the tests that specify it. `docs/SCENARIO_GUIDE.md` for Level 2, `docs/TRACE_FORMAT.md` when you open a trace.
4. `samples/`: real result files and traces to try your tools on.

Quick start, from this folder (Python 3.10 or newer; on Windows use `python` instead of `python3`):

```
python3 -m unittest discover -s tests -t .      # at first every test fails: that is the starting line
```

**Start Phase 3 after your Phase 2 work has been graded.** Your own agent stays in its own repository; this folder is a new repository (ask us where to push). You do not need a model key: see `docs/NO_AZURE.md`. If you do run an agent, put its model settings in a `.env` in this folder (never commit it); the runner reads it for you. Before every commit run `python3 tools/precommit_check.py` (inside a git repository).

All people, records and numbers are fictional.
