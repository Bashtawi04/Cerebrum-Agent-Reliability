"""Apply this reviewed file set to an existing lab, preserving local evidence and Git history."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def digest(data, name):
    if not name.endswith('.zip'):
        data = data.replace(b'\r\n', b'\n')
    return hashlib.sha1(data).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--destination', type=Path, required=True)
    p.add_argument('--apply', action='store_true')
    args = p.parse_args()
    destination = args.destination.resolve()
    if destination == ROOT or not (destination / 'tools/reproduce.py').is_file():
        raise SystemExit('Choose the existing Phase 3 project folder, not this extracted update folder.')
    manifest = json.loads((ROOT / 'tools/release_update.json').read_text(encoding='utf-8'))
    changes = []
    for name, hashes in manifest.items():
        rel = Path(name)
        if rel.is_absolute() or '..' in rel.parts:
            raise SystemExit('Invalid release path')
        source, target = ROOT / rel, destination / rel
        if destination not in target.resolve().parents:
            raise SystemExit('Destination path escapes the project')
        if digest(source.read_bytes(), name) != hashes['new']:
            raise SystemExit(f'Update content mismatch: {name}')
        existing = digest(target.read_bytes(), name) if target.exists() else None
        if existing == hashes['new']:
            continue
        if existing != hashes['old']:
            raise SystemExit(f'Local changes found in {name}; nothing copied. Keep them and share this message.')
        changes.append((name, source, target))
    print(f'{len(changes)} reviewed files to update. Other files and Git history are untouched.')
    if not args.apply or not changes:
        return
    backup = Path(tempfile.mkdtemp(prefix='phase3-before-review-update-'))
    with zipfile.ZipFile(backup / 'before.zip', 'w', zipfile.ZIP_DEFLATED) as z:
        for name, _, target in changes:
            if target.exists():
                z.write(target, name)
    (backup / 'new-files.json').write_text(json.dumps([name for name, _, target in changes if not target.exists()], indent=2))
    for name, source, target in changes:
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
    print(f'Backup: {backup}')
    print('Update applied. Run python tools/reproduce.py from the destination. Nothing pushed.')


if __name__ == '__main__':
    main()
