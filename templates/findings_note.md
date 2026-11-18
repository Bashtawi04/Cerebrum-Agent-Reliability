# Findings: <target track> agent, evaluated by <your name>

Sent to the owner of the agent. Plain, specific, no scores. Keep each finding short enough to read in a minute.

## What I tested
* The agent: repository and commit (`targets/...` is a frozen copy), the model deployment, Python version.
* How many runs of which scenarios (public, the owner's own, mine). The exact commands, so the owner can repeat them.

## What worked
Two or three things, with evidence. A finding list with nothing good in it makes people stop reading.

## Findings
One block per finding, most serious first.

### 1. <short title>
* **Severity** S1 / S2 / S3 / S4 and **label** F1 to F10 (see `docs/TAXONOMY.md` for both).
* **How to see it**: scenario id and command, or the exact messages to send. It must be reproducible by someone else.
* **Expected** and **got**: one sentence each.
* **Evidence**: trace file name and the step number, and how often it happened (for example "3 of 10 runs").
* **My guess at the cause**, clearly marked as a guess if you did not read the code. If you did, point at the file and line.
* **A direction** (optional): what might fix it.

## What I could not tell
Things you suspect but could not reproduce, and what you would need to find out.
