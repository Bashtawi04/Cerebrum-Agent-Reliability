"""Measure the existing Onboarding agent, without copying it into this lab.

Run with --dry-run to inspect the plan without calling a model. A normal run
makes one model-identification request, then executes the selected live suite.
Public: eight cases x ten repeats. Additional: three new cases x three repeats.
Every run uses the supplied harness and fresh database/state. No credentials
are written to the report. The original agent and harness are never edited.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shlex
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from harness.run_scenarios import read_env_file
from lab.aggregate import render_markdown, summarise

PROBE = r'''
import importlib.metadata
import json
import os
import platform
from openai import OpenAI
endpoint = os.environ['AZURE_OPENAI_ENDPOINT'].rstrip('/')
if not endpoint.endswith('/openai/v1'):
    endpoint += '/openai/v1'
try:
    with OpenAI(base_url=endpoint+'/', api_key=os.environ['AZURE_OPENAI_API_KEY'],
                timeout=45, max_retries=2) as client:
        answer = client.chat.completions.create(
            model=os.environ['AZURE_OPENAI_DEPLOYMENT'],
            messages=[{'role':'user', 'content':'Reply with OK.'}])
    print(json.dumps({'model_reported_by_preflight': answer.model,
                      'deployment': os.environ['AZURE_OPENAI_DEPLOYMENT'],
                      'agent_python': platform.python_version(),
                      'openai_sdk': importlib.metadata.version('openai'),
                      'temperature': 'not explicitly set; service default'}))
except Exception as exc:
    # Do not print service messages that may contain account or request details.
    print(json.dumps({'preflight_error_type': type(exc).__name__}))
    raise SystemExit(1)
'''


def git_blob_id(path):
    data = path.read_bytes()
    return hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()


def source_fingerprints(agent_dir):
    paths = [agent_dir / 'agent_cli.py', agent_dir / 'request_plan.py',
             agent_dir / 'requirements.txt']
    for folder in ('peoplehub', 'tools'):
        paths.extend((agent_dir / folder).rglob('*.py'))
        paths.extend((agent_dir / folder).rglob('*.csv'))
    return {p.relative_to(agent_dir).as_posix(): git_blob_id(p)
            for p in sorted(set(paths)) if p.is_file()}


def inspect_results(entries, ids, repeats):
    """A harness exit code of zero alone is not evidence of passing runs."""
    if len(entries) != len(ids) or [row['id'] for row in entries] != ids:
        raise ValueError('Result scenarios do not match the requested suite')
    for row in entries:
        runs = row.get('detail', [])
        if row.get('runs') != repeats or len(runs) != repeats:
            raise ValueError('Missing or incomplete repeated runs')
        if row.get('passes') != sum(run.get('passed') is True for run in runs):
            raise ValueError('Pass total does not match individual runs')
    return all(row['passes'] == repeats and not row.get('violations')
               and all(not run.get('violations') for run in row['detail']) for row in entries)


def agent_command(python):
    # The supplied harness uses shlex.split on all platforms, not a shell.
    return shlex.join([Path(python).as_posix(), '-X', 'utf8', 'agent_cli.py'])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--agent-dir', type=Path, default=Path.home() / 'Downloads/yahya-onboarding-repo/phase2')
    parser.add_argument('--agent-python', type=Path)
    parser.add_argument('--suite', choices=('public', 'additional'), default='public')
    parser.add_argument('--out-dir', type=Path)
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    agent_dir = args.agent_dir.expanduser().resolve()
    python = (args.agent_python or agent_dir / ('.venv/Scripts/python.exe' if os.name == 'nt' else '.venv/bin/python')).resolve()
    for p in (agent_dir / 'agent_cli.py', python):
        if not p.is_file():
            parser.error(f'Missing {p}; point --agent-dir and --agent-python at your existing Phase 2 installation.')
    scenarios = ROOT / 'scenarios' / ('onboarding_public.jsonl' if args.suite == 'public' else 'lab_onboarding.jsonl')
    ids = [json.loads(line)['id'] for line in scenarios.read_text(encoding='utf-8').splitlines() if line.strip()]
    repeats = 10 if args.suite == 'public' else 3
    print(f'{args.suite}: {len(ids)} scenarios x {repeats} = {len(ids)*repeats} live runs, one job at a time.', flush=True)
    print(f'Existing agent: {agent_dir}', flush=True)
    if args.dry_run:
        print('Dry run only. No model calls or files written.')
        return
    env = dict(os.environ)
    for key, value in read_env_file(agent_dir / '.env').items():
        env.setdefault(key, value)
    env.update(PYTHONUTF8='1', PYTHONIOENCODING='utf-8')
    required = ('AZURE_OPENAI_ENDPOINT', 'AZURE_OPENAI_API_KEY', 'AZURE_OPENAI_DEPLOYMENT')
    missing = [key for key in required if not env.get(key)]
    if missing:
        parser.error('Missing configuration: ' + ', '.join(missing) + '. Keep credentials in the Phase 2 .env file.')
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    out = (args.out_dir or ROOT / 'reports/onboarding' / f'{stamp}-{args.suite}').resolve()
    if out.exists():
        parser.error(f'Output already exists; no previous evidence overwritten: {out}')
    before = source_fingerprints(agent_dir)
    print('Checking the configured deployment and recording its reported model...', flush=True)
    probe = subprocess.run([str(python), '-X', 'utf8', '-c', PROBE], cwd=agent_dir,
                           env=env, capture_output=True, text=True, encoding='utf-8', timeout=180)
    try:
        metadata = json.loads(probe.stdout)
    except ValueError:
        raise SystemExit('Model preflight failed before evaluation. Check the existing Phase 2 interpreter and dependencies.')
    if probe.returncode or not metadata.get('model_reported_by_preflight'):
        raise SystemExit('Model preflight failed: ' + metadata.get('preflight_error_type', 'model not reported'))
    out.mkdir(parents=True)
    metadata.update(started_utc=stamp, suite=args.suite, repeats_per_scenario=repeats,
                    source_git_blob_sha1=before, scenario_git_blob_sha1=git_blob_id(scenarios),
                    harness_git_blob_sha1=git_blob_id(ROOT / 'harness/run_scenarios.py'),
                    status='started; not yet evaluated')
    def save_metadata():
        (out / 'metadata.json').write_text(json.dumps(metadata, indent=2) + '\n', encoding='utf-8')
    save_metadata()
    results = out / 'results.json'
    command = [sys.executable, '-X', 'utf8', str(ROOT / 'harness/run_scenarios.py'),
               '--track', 'onboarding', '--agent', agent_command(python),
               '--agent-dir', str(agent_dir), '--scenarios', str(scenarios),
               '--repeat', str(repeats), '--trace-dir', str(out / 'traces'), '--out', str(results), '-v']
    try:
        subprocess.run(command, cwd=ROOT, env=env, check=True)
        entries = json.loads(results.read_text(encoding='utf-8'))
        all_passed = inspect_results(entries, ids, repeats)
        if source_fingerprints(agent_dir) != before:
            raise ValueError('Agent files changed during the run; do not use this as a single-revision result')
        count = sum(row['passes'] for row in entries)
        total = sum(row['runs'] for row in entries)
        title = f'Own Onboarding agent: {args.suite}'
        table = render_markdown(summarise([entries]), title)
        description = ('Model reported by deployment preflight: `' + metadata['model_reported_by_preflight'] +
                       '`. Each scenario was run ' + str(repeats) + ' times. '
                       'Deployment routing was not independently checked on each call.\n\n')
        (out / 'summary.md').write_text(description + table + '\n', encoding='utf-8')
        metadata.update(status='complete', passes=count, runs=total, all_passed=all_passed)
        save_metadata()
        print(f'FINISHED: {count}/{total}. Evidence: {out}', flush=True)
        print('Keep failures and inspect their traces. Do not overwrite them with a cherry-picked rerun.', flush=True)
        if not all_passed:
            raise SystemExit(2)
    except (Exception, KeyboardInterrupt) as exc:
        metadata.update(status='incomplete', failure_type=type(exc).__name__)
        save_metadata()
        raise


if __name__ == '__main__':
    main()
