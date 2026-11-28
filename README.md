# Agent Reliability Lab — Learning evidence

**Yahya AlBashtawi · Cerebrum · Phase 3**

This second review adds ten scenarios, predictions, scripted controls and trace-based findings to the lab core. It incorporates the thirty Learning Coach runs returned by the mentors on 25 November. The frozen target is `5f4d9dc`; no target code changes are included.

[Findings](reports/findings_learning.md) · [Evaluation report](reports/evaluation_report.md) · [New evidence](reports/learning/review.md) · [Scenario validation](reports/scenario_validation.md) · [Review branches](reports/review_branches.md)

## Reproduce

Python 3.10+ and Git; no packages or credentials required.

Windows / PowerShell:

```powershell
python -X utf8 tools/reproduce.py
```

Linux/macOS:

```bash
python3 -X utf8 tools/reproduce.py
```

This branch runs 64 tests, validates ten scenarios, verifies thirty returned traces and 232 protected input files, reproduces the earlier tables/gate, checks all 26 earlier failure labels, and runs the good/bad scripted experiments. No model calls occur.

## Evidence

| Suite | Result | Meaning |
|---|---:|---|
| Earlier public recordings | 94/96 | Twelve repeats per case |
| Earlier colleague recordings | 0/24 | Different cases, not a before/after change |
| New mentor target runs | 18/30 | Original submitted assertions, preserved |
| Same new traces after revising LAB-LRN-06 | 17/30 | Offline replay of changed assertions, not a new experiment |

Model: mentors' `gpt-5.4-mini`; an exact model revision was not supplied. No target safety violations were reported. The original and revised [tables](reports/learning/) include per-case Wilson intervals. Three successes remain statistically unproven.

The new findings show a dropped learning-plan draft and malicious catalogue instructions copied into approval text. The original 06 test required a particular lookup route; the shared revised capability scenario checks the message instead while retaining approval protection. Its card preserves the original prediction and labels the revision as post-observation. The prior predictions remain unchanged in `reports/predictions.json`, historically committed at `50bf3f7` in the original review branch.

Two fixture cases distinguish correct from deliberately broken behaviour. Raw fixture data are folded by default in GitHub's diff but retained; these are not target scores. The target archive is preserved unchanged with per-member fingerprints.

Onboarding evidence, its provenance corrections and the final review response are in `phase3-onboarding-review`, the third dependent branch. Incoming peer review and hosted CI for these new heads remain separate steps.
