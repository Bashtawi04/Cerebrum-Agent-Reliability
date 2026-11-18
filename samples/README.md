# Sample data to build and test your lab tools on

* `results_<track>_reference_a.json` and `..._b.json`: two real runner `--out` files for each track, from our own reference agent
  (a LangGraph agent, three runs of every public scenario each). Some scenarios are flaky on purpose: that is real model variance.
  Try `python -m lab.aggregate samples/results_recruiting_reference_a.json samples/results_recruiting_reference_b.json` once you have
  written `summarise` and `render_markdown`: the two files merge into six runs per scenario.
* `traces/scripted_good/` and `traces/scripted_claims_done/`: the same four public onboarding scenarios run by a scripted
  agent that behaves correctly, and by one that says "I have raised it" before anything is raised. Your honesty checker must
  stay silent on the first folder and speak up on three of the four in the second (the fourth, OB-06, really did write a note, so
  its "Done" is true).
* `traces/reference_agent/`: three traces from a real model agent (the Recruiting examples in `scenarios/examples_recruiting.jsonl`).

Open a trace with any JSON viewer and follow `docs/TRACE_FORMAT.md`.
