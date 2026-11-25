# Agent Reliability Lab

**Yahya AlBashtawi · Cerebrum · Phase 3**

This lab tests whether an agent finishes the requested work, respects approval boundaries and describes its actions accurately. It combines repeated-run statistics, database effects, full conversation traces and manual failure analysis.

The frozen **Learning Coach (`5f4d9dc`)** is the main review target. My **Onboarding agent** is evaluated separately. Both use fictional PeopleHub data. This repository contains evaluation code and evidence; it does not replace either agent.

[Evaluation report](reports/evaluation_report.md) · [Learning findings](reports/findings_learning.md) · [Mentor review response](reports/mentor_review_response.md) · [Delivery status](reports/phase3_status.md)

## Reproduce locally

Python **3.10+**, Git and the standard library are sufficient. No API key or package installation is needed for offline checks.

From the repository root on Windows / PowerShell:

```powershell
python -X utf8 tools/reproduce.py
```

On Linux / macOS:

```bash
python3 -X utf8 tools/reproduce.py
```

The full package checks **77 unit tests**, ten Learning and three Onboarding scenarios, protected-input fingerprints, original and revised evidence tables, failure classifications, the regression gate, honesty controls and fresh scripted experiments. The 47 supplied tests and 232 protected input files remain unchanged.

A successful command ends with `OFFLINE CHECKS PASSED`. It verifies this code and the saved evidence; it does not make new model calls, complete peer review or establish reliability on every possible request.

## Results and their limits

| Evidence | Result | Interpretation |
|---|---:|---|
| Supplied Learning public recordings | 94/96 | Eight cases, twelve repeats each |
| Supplied Learning colleague recordings | 0/24 | Different cases; not a before/after comparison |
| Mentor runs of my ten Learning scenarios, 25 November | 18/30 | Original submitted assertions |
| Same thirty traces with revised LAB-LRN-06 assertions | 17/30 | Offline re-score; the stronger message check exposes contamination |
| Own Onboarding public runs, 22 November | 80/80 | Eight cases, ten repeats each |
| Own Onboarding additional runs | 6/9 original → 9/9 offline | Only the seeded-row correction in OB-03 changes the score |

The Learning batches identify the model as `gpt-5.4-mini`; an exact service revision was not supplied. The Onboarding preflight reports `gpt-5.4-mini-2026-03-17`, deployment `gpt-5.4-mini` in Microsoft Foundry. These measurements are kept separate. Azure subscription/billing ownership is not recorded in the old evidence.

No safety violations were reported in these target or Onboarding batches. The deliberately broken fixture's violations are positive controls, not target-agent results. Each 3/3 case has a Wilson 95% interval of about **0.44–1.00** and remains **unproven**.

## What the review uncovered

- **Dropped work:** a booking can complete while a second booking or requested draft is forgotten. A truthful receipt for one action does not prove the whole request is complete.
- **Misleading approval text:** the Learning Coach copies a malicious catalogue instruction into a manager's approval message, although it still prevents an unauthorised write.
- **Our test defect:** LAB-LRN-06 required one particular lookup API. That rejected an acceptable alternative route and did not test the contaminated approval message. The revised capability case checks the message while retaining the approval and no-write assertions.
- **Our reporting correction:** OB-03's seeded-record count caused the three original Onboarding failures. OB-01 remains 3/3 after its pattern correction. The archived check names disagree with the source scenario copy; that provenance limitation is documented rather than hidden.
- **Checker robustness:** a null trace message is treated as empty text without losing its audit evidence.

The target agent is frozen and has not been edited. Changes to an agent would require separate regression evidence and new live measurements.

## Where to inspect the evidence

| Question | File |
|---|---|
| How do the statistics and earlier recorded failures work? | [Evaluation report](reports/evaluation_report.md), [failure index](reports/failure_index.md) |
| What happened on the ten new scenarios? | [Learning evidence review](reports/learning/review.md), [original table](reports/learning/original_table.md), [revised table](reports/learning/revised_table.md) |
| Which defects should the Learning Coach owner investigate? | [Findings with reproduction, trace and code references](reports/findings_learning.md) |
| What changed in the Onboarding measurement? | [Onboarding review and provenance](reports/onboarding/review.md) |
| What was predicted before the experiments? | [Predictions](reports/predictions.json), [scenario cards](reports/cards/) |
| What does the honesty checker miss? | [Honesty review](reports/honesty_review.md) |
| How was the mentor's feedback addressed? | [Review response](reports/mentor_review_response.md) |

The raw evidence archives retain all original result and trace file contents. Archive manifests verify every member. The Onboarding container was rebuilt with portable entry paths; its original container is retained in Git history. Large, redundant full re-score JSON copies have been removed. Both review scripts recompute the compact derived reports from the original evidence.

## Code map

| Component | Role |
|---|---|
| `lab/stats.py` | Wilson intervals, pass^k and pass@k |
| `lab/aggregate.py` | Per-scenario tables from repeated results |
| `lab/honesty.py` | Three specified claim-versus-audit checks |
| `lab/gate.py` | Detect reported safety violations, missing cases and statistically separated drops |
| `scenarios/` | Shared experiments run by the unchanged harness |
| `scripted/` | Good and deliberately faulty controls |
| `tools/review_learning_evidence.py` | Verify thirty mentor traces; replay the explicit LAB-LRN-06 correction |
| `tools/review_live_evidence.py` | Verify 89 Onboarding traces; reproduce the documented re-score |
| `tools/evaluate_onboarding.py` | Evaluate an explicitly selected separate agent; save consumed scenario bytes and metadata |
| `tools/evidence_archive.py` | Portable archives and content fingerprint verification |
| `tools/reproduce.py` | Offline verification used by CI |

`pass^3` asks whether all three sampled attempts succeed; `pass@3` asks whether at least one succeeds. A passing public A→B gate means no regression was detected under its rules, not equivalence or general agent correctness. The three-rule honesty checker does not measure request completeness, semantic injection resistance or reply language.

## Future live evaluation

Existing results do not need rerunning merely to read this report. For a changed Onboarding agent, explicitly identify its separate environment:

```bash
python tools/evaluate_onboarding.py --agent-dir "/absolute/path/to/phase2" --agent-python "/absolute/path/to/python" --dry-run
```

Only after inspecting the plan, replace `--dry-run` with `--suite public` or `--suite additional`. On Windows use the environment's `Scripts/python.exe`; on Linux/macOS use `bin/python`. An optional non-secret `--resource-owner` label identifies cost responsibility. Live runs consume model quota and run one job at a time.

Each new batch snapshots the exact scenario bytes given to the runner, records their hash, preserves failed results and creates a portable evidence archive. The lab contains no Downloads cleanup, installer or file-moving utility.

## Review and completion status

The mentor approved this separate GitHub repository. [PR #1](https://github.com/Bashtawi04/Cerebrum-Agent-Reliability/pull/1) contains the earlier submission and review context. The revised delivery is separated into [three dependent branches](reports/review_branches.md): lab checks, Learning evidence, then Onboarding evidence. Each has its own reproducible scope; no merge or mentor acceptance is implied.

The previous hosted [CI run](https://github.com/Bashtawi04/Cerebrum-Agent-Reliability/actions/runs/45136982970) passed on Python 3.10 and 3.12 at `9d6a7b7`. Revised branches require their own hosted checks after publication.

Level 3 still needs the peer exchange and responses to incoming Recruiting findings on my Onboarding agent. Abdelrhman will forward those findings when available. The new Learning runs have arrived and are analysed; they are no longer a pending task. Known own-agent reply-quality issues remain visible in the Onboarding review. No demonstration is added as a requirement.
