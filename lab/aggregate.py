"""Turn the runner's --out files into one honest table per scenario."""
import argparse
import json
from collections import Counter
from pathlib import Path
from .models import ScenarioSummary
from .stats import pass_hat_k, wilson_interval

def load_results(path: str | Path) -> list[dict]:
    """Read one file written by `run_scenarios.py --out`: a list with one entry per scenario."""
    return json.loads(Path(path).read_text(encoding='utf-8'))

def summarise(result_files: list[list[dict]], solid_low: float=0.7) -> list[ScenarioSummary]:
    """Merge several runner results (each already loaded with load_results) into one summary per scenario id.

    For every scenario id, in the order each id first appears:
      * runs and passes are the sums of the entries' "runs" and "passes";
      * level is the "level" of the first entry;
      * low, high = wilson_interval(passes, runs);
      * pass_hat_3 = pass_hat_k(passes, runs, 3), or None when runs < 3;
      * top_failures: look at every run in every entry's "detail" list whose "passed" is false, count each of its checks
        whose "ok" is false by its "name" (a name that appears twice in one run counts twice), and keep the three most
        common as (name, count), highest count first, ties in alphabetical order of the name. An entry with no
        "detail" list has no failures to count; a check inside a run that passed is never counted;
      * safety: the sorted distinct values in the entries' "violations" lists;
      * label: "failing" when passes == 0; "flaky" when 0 < passes < runs; otherwise ("unproven" when low < solid_low,
        "solid" when low >= solid_low).
    """
    if not 0 <= solid_low <= 1:
        raise ValueError('solid_low must be between 0 and 1')
    groups = {}
    for entries in result_files:
        for entry in entries:
            wilson_interval(entry['passes'], entry['runs'])
            group = groups.setdefault(entry['id'], {
                'level': entry['level'], 'runs': 0, 'passes': 0,
                'failures': Counter(), 'safety': set(),
            })
            group['runs'] += entry['runs']
            group['passes'] += entry['passes']
            group['safety'].update(entry.get('violations', []))
            for run in entry.get('detail', []):
                if run.get('passed') is False:
                    group['failures'].update(check['name'] for check in run.get('checks', []) if check.get('ok') is False)
    summaries = []
    for sid, group in groups.items():
        passes, runs = group['passes'], group['runs']
        low, high = wilson_interval(passes, runs)
        label = ('failing' if passes == 0 else 'flaky' if passes < runs
                 else 'unproven' if low < solid_low else 'solid')
        summaries.append(ScenarioSummary(
            sid, group['level'], runs, passes, low, high,
            pass_hat_k(passes, runs, 3) if runs >= 3 else None, label,
            sorted(group['failures'].items(), key=lambda pair: (-pair[1], pair[0]))[:3],
            sorted(group['safety']),
        ))
    return summaries

def render_markdown(summaries: list[ScenarioSummary], title: str='Results') -> str:
    """The report table, exactly in this shape (no trailing spaces):

        ## {title}

        | scenario | level | passed | 95% interval | pass^3 | label | most common failing checks |
        |---|---|---|---|---|---|---|
        | LRN-07 | 3 | 7/9 | 0.45-0.94 | 0.42 | flaky | effect enrolments {...} (2); approval requests (1) |

        3 scenarios, 27 runs, 21 passed. Safety: none

    One row per summary, in the given order. Numbers use two decimals; pass^3 is "n/a" when it is None; the last column
    is the top_failures as "name (count)" joined with "; ", or "-" when there are none (do not escape any character in a name). The last line says
    "{n} scenarios, {total runs} runs, {total passes} passed. Safety: " followed by "none", or by the distinct
    violation kinds of all summaries, sorted and joined with ", ".
    """
    lines = [f'## {title}', '',
             '| scenario | level | passed | 95% interval | pass^3 | label | most common failing checks |',
             '|---|---|---|---|---|---|---|']
    for s in summaries:
        chance = 'n/a' if s.pass_hat_3 is None else f'{s.pass_hat_3:.2f}'
        failures = '; '.join(f'{name} ({count})' for name, count in s.top_failures) or '-'
        lines.append(f'| {s.id} | {s.level} | {s.passes}/{s.runs} | {s.low:.2f}-{s.high:.2f} | {chance} | {s.label} | {failures} |')
    safety = ', '.join(sorted({v for s in summaries for v in s.safety})) or 'none'
    lines.extend(['', f'{len(summaries)} scenarios, {sum(s.runs for s in summaries)} runs, '
                  f'{sum(s.passes for s in summaries)} passed. Safety: {safety}'])
    return '\n'.join(lines)

def main() -> None:
    ap = argparse.ArgumentParser(description='Summarise runner --out files into a markdown table.')
    ap.add_argument('results', nargs='+', help='one or more files written by run_scenarios.py --out')
    ap.add_argument('--title', default='Results')
    ap.add_argument('--out', help='write the markdown here instead of printing it')
    ap.add_argument('--tag', help='only scenarios whose "tags" list contains this word, for example regression')
    a = ap.parse_args()
    files = [load_results(p) for p in a.results]
    if a.tag:
        files = [[e for e in entries if a.tag in e.get('tags', [])] for entries in files]
    text = render_markdown(summarise(files), a.title)
    if a.out:
        Path(a.out).write_text(text + '\n', encoding='utf-8')
    else:
        print(text)
if __name__ == '__main__':
    main()
