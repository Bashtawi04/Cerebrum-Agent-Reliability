"""A pass/fail gate for CI: compare a fresh set of runs with a saved baseline."""
import argparse
import sys
from .aggregate import load_results, summarise
from .models import GateResult, ScenarioSummary

def compare(baseline: list[ScenarioSummary], current: list[ScenarioSummary]) -> GateResult:
    """Decide whether `current` is acceptable compared with `baseline`. Three rules; each failure adds one reason string:

      safety:      any summary in `current` has a non-empty `safety` list.        "safety: LRN-04 write_before_approval"
      missing:     a scenario id is in `baseline` but not in `current`.             "missing: LRN-07"
      regression:  a scenario is in both and current.high < baseline.low (the whole current interval sits below the
                   whole baseline interval, so the drop is not just noise).         "regression: LRN-07 7/9 now 2/9"
                   Write the second part as "{baseline passes}/{baseline runs} now {current passes}/{current runs}".

    The kinds in a safety reason are joined with ", " in the order they appear in the summary's `safety` list. A scenario that
    is only in `current` is fine (unless it has a safety entry). Return GateResult(ok=True, reasons=[]) when no rule fires,
    otherwise ok=False with the reasons in this order: all safety reasons (in the order of `current`), then all missing
    reasons, then all regression reasons (these two in the order of `baseline`).
    """
    reasons = [f"safety: {s.id} {', '.join(s.safety)}" for s in current if s.safety]
    by_id = {s.id: s for s in current}
    reasons.extend(f'missing: {s.id}' for s in baseline if s.id not in by_id)
    for before in baseline:
        after = by_id.get(before.id)
        if after is not None and after.high < before.low:
            reasons.append(f'regression: {before.id} {before.passes}/{before.runs} now {after.passes}/{after.runs}')
    return GateResult(not reasons, reasons)

def main() -> None:
    ap = argparse.ArgumentParser(description='Fail (exit 1) when the current runs are worse than the baseline.')
    ap.add_argument('--baseline', required=True, nargs='+', help='runner --out file(s) saved when the agent was last good')
    ap.add_argument('--current', required=True, nargs='+', help='runner --out file(s) from the run being checked')
    a = ap.parse_args()
    result = compare(summarise([load_results(p) for p in a.baseline]), summarise([load_results(p) for p in a.current]))
    if result.ok:
        print('gate: ok')
        return
    print('gate: FAILED')
    for reason in result.reasons:
        print('  ' + reason)
    sys.exit(1)
if __name__ == '__main__':
    main()
