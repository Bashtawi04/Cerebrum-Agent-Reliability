## Summary

This adds the Phase 3 reliability lab for the frozen Learning Coach. It measures repeated-run consistency, checks replies against audit evidence and records why failed requests did not finish.

The supplied public recordings pass 94/96 runs (Wilson 95% interval 0.927–0.994), while the colleague suite passes 0/24 (0.000–0.138). Both use the mentors' recorded gpt-5.4-mini deployment. The report traces all 26 failures to evidence and keeps these suites separate.

## Changes

- Implemented the four lab modules and kept the supplied tests, target, harness and PeopleHub unchanged.
- Added ten scenarios, with predictions committed before the experiments.
- Demonstrated two scenarios accepting correct fixtures and rejecting deliberately broken variants.
- Added the evaluation report, honesty controls, five review findings and an offline CI workflow.
- Added a reversible organizer for known old Phase 2 downloads; it does not change working repositories.

## Validation

`python tools/reproduce.py` passes locally: 72 unit tests, scenario validation, secret/generated-file check, protected-input checks, recorded-report reproduction, failure-index coverage, honesty controls, public A/B gate and scripted experiments. A fresh local clone was also checked.

The correct fixtures each pass 3/3 (95% interval 0.44–1.00); the broken fixtures each pass 0/3 (0.00–0.56). These are model-free checks, not target-model results.

## Remaining work

The new Learning Coach scenarios still need target-model runs from the mentors. The own Onboarding evaluation is now recorded: 80/80 public runs, and 6/9 original additional runs. Two scenario defects are documented and regression-tested; an offline re-score of the same additional traces passes 9/9. Original evidence is retained. Wrong-language and unwanted-offer findings remain open; the agent was not changed. Incoming Phase 3 findings and reciprocal review remain pending. Hosted push checks passed on Python 3.10 and 3.12 at `fd2e33d`; verify the next run after the action-version update. The current report does not claim a target fix, a new-model score or mentor acceptance.
