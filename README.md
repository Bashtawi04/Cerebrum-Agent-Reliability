# Agent Reliability Lab

**Yahya AlBashtawi · Cerebrum · Phase 3**

A reproducible evaluation of whether an AI agent finishes the requested work, respects approval boundaries and accurately describes what happened.

[Evaluation report](reports/evaluation_report.md) · [Review findings](reports/findings_learning.md) · [Technical guide](docs/PROJECT_GUIDE.md) · [Delivery checklist](reports/phase3_status.md) · [GitHub Actions](https://github.com/Bashtawi04/Cerebrum-Agent-Reliability/actions)

---

## Why this project exists

An agent can pass a scenario and still omit part of a request, describe a proposed action as completed, or fail when the same request is repeated. This lab checks the database effects and conversation together, then measures how consistently the agent succeeds.

Phase 1 built an onboarding assistant that answers from documents and permitted records. Phase 2 added controlled actions and human approval. **Phase 3 evaluates reliability:** it is a separate project, not a replacement for either earlier implementation.

The main target is the supplied **Learning Coach**, frozen at commit `5f4d9dc`. My own **Onboarding agent** is measured separately. Both use fictional PeopleHub data; no real HR records are changed and no external emails are sent.

## Start here

| What you want to inspect | Open |
|---|---|
| Measurements, model information and limitations | [Evaluation report](reports/evaluation_report.md) |
| Why the Learning Coach failed | [Five findings with trace and code references](reports/findings_learning.md) |
| The original and corrected Onboarding results | [Evidence review](reports/onboarding/review.md) |
| The ten new Learning Coach experiments | [Scenario file](scenarios/lab_learning.jsonl) and [prediction cards](reports/cards/) |
| How the code and statistics work | [Project guide](docs/PROJECT_GUIDE.md) |
| Completed work and remaining review steps | [Delivery status](reports/phase3_status.md) |

## Reproduce the work

The offline lab needs **Git and Python 3.10 or newer**. It uses the Python standard library: no API key, Azure connection or package installation is required.

```bash
git clone --branch phase3-reliability https://github.com/Bashtawi04/Cerebrum-Agent-Reliability.git
cd Cerebrum-Agent-Reliability
```

**Windows / PowerShell:**

```powershell
python -X utf8 tools/reproduce.py
```

**Linux / macOS:**

```bash
python3 -X utf8 tools/reproduce.py
```

The command checks all 72 unit tests, both new scenario files, preserved live evidence, the secret/generated-file scan, 232 protected inputs, report reproduction, all failed-run classifications, honesty controls, the baseline/current gate and fresh scripted experiments. Successful execution ends with `OFFLINE CHECKS PASSED`.

This reproduces saved evidence and model-free experiments. It does **not** make new model calls or prove that a changed agent would obtain the same live results.

## Evidence at a glance

### Supplied Learning Coach recordings

Model: mentor-recorded **`gpt-5.4-mini`**. The suites below contain different requests; they are not before/after measurements.

| Suite | Runs | Passed | Pooled Wilson 95% interval | Evidence |
|---|---:|---:|---|---|
| Public: eight scenarios, 12 repeats each | 96 | 94/96 | 0.927–0.994 | [Per-scenario table](reports/target_table.md) |
| Colleague: four scenarios, six repeats each | 24 | 0/24 | 0.000–0.138 | [Per-scenario table](reports/colleague_table.md) |

Pooled intervals summarize these samples; they do not account for arbitrary real-world task mixtures or correlated runs. The linked tables include per-scenario intervals, `pass^3` and failure labels.

- **26/26 failed runs classified**, with a trace, step and relevant code reference.
- **120 traces checked** by the three-rule honesty checker, with zero findings on those target recordings.
- Positive controls detect three supplied false claims and one synthetic false claim; seven clean controls remain clear.
- The public A → B gate passes: **no regression detected under its rules**, not a claim that the colleague suite passes.

### Own Onboarding agent

Model-identification response: **`gpt-5.4-mini-2026-03-17`**. These runs were made on Windows on 22 November 2026 and are kept separate from the target recordings.

| Evaluation | Recorded result | Per-scenario uncertainty |
|---|---|---|
| Public: eight cases × ten repeats | **80/80 live runs** | Each 10/10: Wilson 95% approximately 0.72–1.00 |
| Additional: three cases × three repeats | **6/9 original live runs** | See the [original table](reports/onboarding/additional_original_table.md) |
| Same additional traces after correcting our checks | **9/9 offline re-score** | Each 3/3: approximately 0.44–1.00; unproven |

The additional check incorrectly treated an existing laptop record as a new action. Two reply patterns were also incorrectly escaped. The corrections have regression tests, and the original results and traces are preserved. **The re-score is not a new live run or an agent improvement.**

The harness reported zero safety violations across these 89 runs. Manual review still found wrong-language output, unwanted follow-up offers and repetition of an unverified approval claim. Those findings remain open; passing assertions do not establish perfect replies.

## How the lab works

```mermaid
flowchart TD
    A[Scenario and agent] --> B[Supplied runner]
    B --> C[Database checks and results]
    B --> D[Conversation and audit traces]
    C --> E[Statistics and regression gate]
    D --> F[Honesty checker and manual review]
    E --> G[Evidence report]
    F --> G
    G --> H[New regression scenarios]
    H --> A
```

| Component | Responsibility |
|---|---|
| `lab/stats.py` | Wilson intervals, `pass^k`, `pass@k` and input validation |
| `lab/aggregate.py` | Combine result files into per-scenario summaries |
| `lab/honesty.py` | Compare specified reply claims with successful writes and approval status |
| `lab/gate.py` | Reject reported safety violations, missing scenarios and statistically separated drops |
| `scenarios/lab_learning.jsonl` | Ten new target experiments with prior predictions |
| `scripted/` | Predictable correct and deliberately broken behaviours for testing scenarios |
| `reports/` | Results, classifications, findings, predictions and original evidence |
| `tools/reproduce.py` | One-command offline verification |
| `.github/workflows/offline-checks.yml` | Run offline verification on Python 3.10 and 3.12 |

The supplied target, PeopleHub implementation, harness and original tests remain unchanged. Protected file hashes are checked during reproduction.

## What the new scenarios establish

The ten Learning Coach cases cover multi-action requests, refused actions, approval recovery, instructions hidden in data and other boundary conditions. Predictions were committed at `50bf3f7` before the scripted experiments.

Two cases were exercised with correct and deliberately broken fixtures. Correct behaviours pass **3/3 per case**; broken behaviours pass **0/3 per case**. The respective Wilson 95% intervals are approximately **0.44–1.00** and **0.00–0.56**. These are **fixture results, not target-model scores**.

The ten new cases still need target-model execution. The brief provides a mentor-run route: send [the validated scenario file](scenarios/lab_learning.jsonl) and request results plus full traces. See [model-access instructions](docs/NO_AZURE.md).

## Reading the results correctly

- A proposal is not an executed action. An open laptop request is not a delivered laptop.
- `pass^3` measures whether all three sampled attempts pass; `pass@3` asks whether at least one passes. For action agents, consistency matters.
- Three successes are labelled **unproven** because the uncertainty is wide.
- Zero honesty findings means none of the checker's three patterns fired. It does not verify every action, detail or language.
- A successful CI run checks code and committed evidence. It does not run Azure or certify the agent's behaviour on unseen requests.

## Live evaluations and useful commands

The completed own-agent batches do not need to be repeated merely to reproduce this report. For a future agent revision, use the helper below, one job at a time:

```bash
python tools/evaluate_onboarding.py --dry-run
python tools/evaluate_onboarding.py --suite public
python tools/evaluate_onboarding.py --suite additional
```

On Linux/macOS use `python3`. The helper defaults to the separate Windows Phase 2 checkout at `~/Downloads/yahya-onboarding-repo/phase2`. Elsewhere, pass `--agent-dir` and `--agent-python` with absolute paths. The target agent has its own dependencies and model configuration; these live commands consume model quota. Keep new evidence separate from the original batches.

For individual offline checks:

```bash
python -m unittest discover -s tests -t . -v
python tools/validate_scenarios.py scenarios/lab_learning.jsonl --track learning
python -m lab.honesty recorded/learning_agent/traces
python -m lab.gate --baseline recorded/learning_agent/public_a.json --current recorded/learning_agent/public_b.json
python tools/precommit_check.py
```

## Publication and review

The mentor approved GitHub for this separate repository. Both `main` and `phase3-reliability` are published. The latter contains the current evaluation package; `main` retains the runnable foundation until review and merge.

[Hosted push run 45133818132](https://github.com/Bashtawi04/Cerebrum-Agent-Reliability/actions/runs/45133818132) passed on Python 3.10 and 3.12 at `fd2e33d`. This documentation revision also updates the GitHub action versions; its hosted result must be checked separately after pushing.

**Level 1–2 technical work is ready for review.** [PR #1](https://github.com/Bashtawi04/Cerebrum-Agent-Reliability/pull/1) is open. Remaining delivery work is the human review exchange and confirmation of the next CI run. Level 3 still needs new target-model evidence and responses to incoming findings. The review rotation is **Onboarding → Learning Coach; Recruiting → Onboarding**. No mentor acceptance is claimed.

[Prepared PR description](reports/PR_DESCRIPTION.md) · [Mentor handover message](reports/mentor_message.md) · [Phase 2 handover](docs/PHASE2_HANDOVER.md)

The optional `tools/organize_downloads.py` previews known old Phase 2 downloads for reversible archiving; `--apply` moves them and records an undo manifest. It does not delete the working repositories. No cleanup run is claimed here.
