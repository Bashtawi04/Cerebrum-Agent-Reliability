# Reliability report: <track> agent

Your name, date, commit of the agent you measured (`git rev-parse --short HEAD`).

## Setup (so someone else can repeat it)
* Agent commit, Python version, model deployment, the exact runner command(s). Number of runs per scenario.
* What was the same in every run (fresh database, empty state folder), and anything that was not.

## The numbers
Paste the table from `python -m lab.aggregate ...` here (public scenarios, then your own). Then, in your own words:
* Which scenarios are `solid`, `unproven`, `flaky`, `failing`. Which ones surprised you.
* The pass^3 of the whole public set (the average of the per-scenario values) and what it means for someone who relies on this agent.

## Every failing run, classified
One row per failing run or per group of identical failures. Use the labels in `docs/TAXONOMY.md`.

| Scenario | Runs affected | Label | What happened (one sentence) | Cause, and how sure you are | Evidence (trace file) |
|---|---|---|---|---|---|

## What the honesty checker found
How many traces, how many findings, which rules. For each finding: was it a real false claim, or a false alarm of the checker? If
a false alarm, say how you would change the rule.

## What I changed and what it did
Only changes made because of this report. For each: the failure it addresses, the change (commit), the numbers before and after
on the same scenarios and the same number of runs.

## What I did not check
Be specific: one model only, no concurrency, nothing about cost, ...
