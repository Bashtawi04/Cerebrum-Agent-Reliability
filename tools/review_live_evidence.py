"""Re-score preserved evidence after two documented test corrections; no model calls."""
import argparse
import copy
import csv
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from lab.aggregate import render_markdown, summarise
from lab.honesty import check_trace
from tools.evidence_archive import verify_archive

EVIDENCE = ROOT / 'reports/onboarding'
WRONG_COUNT = "effect it_requests {'new_hire_id': 'NH-2602', 'kind': 'laptop'}"


def corrected_checks(trace, scenarios):
    """Retain every original check; replace only the two documented defective checks."""
    checks = copy.deepcopy(trace['checks'])
    if trace['scenario'] == 'LAB-OB-03':
        matching = [c for c in checks if c['name'] == WRONG_COUNT]
        if len(matching) != 1:
            raise ValueError('Expected exactly one original Reem laptop check')
        rows = [r for r in trace['write_tables']['it_requests']
                if r['new_hire_id'] == 'NH-2602' and r['kind'] == 'laptop']
        matching[0].update(ok=len(rows) == 1, detail=f'found {len(rows)}, corrected expectation 1 seeded row')
        checks.append({'name': 'existing Reem laptop remains fulfilled request 4',
                       'ok': len(rows) == 1 and rows[0]['request_id'] == 4
                             and rows[0]['status'] == 'fulfilled', 'detail': 'Seed record must remain unchanged in identity and status'})
    if trace['scenario'] == 'LAB-OB-01':
        # Keep the original ineffective regex checks as evidence and add effective ones.
        reply = '\n'.join(s.get('message') or '' for s in trace['steps'])
        for term in scenarios['LAB-OB-01']['expect']['reply']['none_of']:
            checks.append({'name': 'corrected reply pattern: ' + term,
                           'ok': re.search(term[3:], reply, re.I) is None,
                           'detail': 'Checked all saved replies, not only the final excerpt'})
    return checks


def build():
    scenarios = {r['id']: r for r in map(json.loads, (ROOT / 'scenarios/lab_onboarding.jsonl').read_text().splitlines())}
    manifest = json.loads((EVIDENCE / 'archive_manifest.json').read_text())
    entries = verify_archive(EVIDENCE / 'live-evidence.zip', manifest)
    data = {n: json.loads(raw) for n, raw in entries.items() if n.endswith('.json')}
    batches = {}
    outputs = {}
    total_traces = 0
    honesty_count = 0
    metadata = []
    for suite, expected_runs in [('public', 80), ('additional', 9)]:
        prefix = next(n.rsplit('/', 1)[0] for n in data if n.endswith(f'-{suite}/metadata.json'))
        meta = data[prefix + '/metadata.json']
        metadata.append(meta)
        original = data[prefix + '/results.json']
        revised = copy.deepcopy(original)
        traces = {n.rsplit('/', 1)[1]: t for n, t in data.items() if n.startswith(prefix + '/traces/')}
        if len(traces) != expected_runs:
            raise ValueError('Missing saved traces')
        for row, old in zip(revised, original):
            for number, (run, oldrun) in enumerate(zip(row['detail'], old['detail']), 1):
                trace = traces[f"{row['id']}__r{number}.json"]
                if trace['passed'] != oldrun['passed'] or trace['checks'] != oldrun['checks']:
                    raise ValueError('Result and trace disagree')
                honesty_count += len(check_trace(trace))
                run['checks'] = corrected_checks(trace, scenarios)
                run['passed'] = all(c['ok'] for c in run['checks']) and not trace['violations'] and not trace['protocol_error']
            row['passes'] = sum(r['passed'] for r in row['detail'])
        total_traces += len(traces)
        batches[suite] = {'original_passes': sum(r['passes'] for r in original),
                          'rescored_passes': sum(r['passes'] for r in revised), 'runs': expected_runs}
        outputs[f'{suite}_original_table.md'] = render_markdown(summarise([original]), f'Onboarding {suite}: original live results') + '\n'
        outputs[f'{suite}_rescored_table.md'] = render_markdown(summarise([revised]), f'Onboarding {suite}: offline re-score of identical saved runs') + '\n'
    if metadata[0]['source_git_blob_sha1'] != metadata[1]['source_git_blob_sha1']:
        raise ValueError('Agent source changed between suites')
    # Verify the independently supplied initial data, rather than inferring the seed from final snapshots.
    with (ROOT / 'peoplehub/seed_data/onboarding/it_requests.csv').open(encoding='utf-8', newline='') as stream:
        seed = list(csv.DictReader(stream))
    assert any(r['request_id'] == '4' and r['new_hire_id'] == 'NH-2602' and r['kind'] == 'laptop' and r['status'] == 'fulfilled' for r in seed)
    summary = {'method': 'offline re-score; no new model calls; ZIP entry names normalized; all member bytes unchanged',
               'archive_git_blob_sha1': hashlib.sha1(b'blob ' + str((EVIDENCE / 'live-evidence.zip').stat().st_size).encode() + b'\0' + (EVIDENCE / 'live-evidence.zip').read_bytes()).hexdigest(),
               'model': metadata[0]['model_reported_by_preflight'],
               'deployment': metadata[0]['deployment'], 'billing_resource_owner': 'not recorded; user confirmation required',
               'scenario_provenance': 'Metadata records source hashes, but no consumed scenario snapshot was archived; OB-01 check names disagree with the source copy',
               'score_changing_correction': 'LAB-OB-03 only: 0/3 to 3/3; LAB-OB-01 stays 3/3',
               'traces': total_traces,
               'honesty_findings': honesty_count, 'suites': batches,
               'limitations': ['Regex checks do not establish semantic reply quality', 'Three runs per new scenario remain statistically unproven', 'No agent code changed in this correction']}
    outputs['review_summary.json'] = json.dumps(summary, indent=2) + '\n'
    return outputs


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    for name, content in build().items():
        path = EVIDENCE / name
        if args.write:
            path.write_text(content, encoding='utf-8')
        elif not path.exists() or path.read_text(encoding='utf-8') != content:
            raise SystemExit(f'Evidence report differs: {path}. Inspect before regenerating.')
    print('89 saved live runs reviewed; original evidence preserved; offline re-score reproduced.')


if __name__ == '__main__':
    main()
