"""Archive known Phase 2 downloads, reversibly. Never alters a working repository.

Preview: python tools/organize_downloads.py
Apply:   python tools/organize_downloads.py --apply
Undo:    python tools/organize_downloads.py --undo PATH_TO_MANIFEST
"""
import argparse
from datetime import datetime
import json
import os
from pathlib import Path
import re
import stat

PACKAGES = {
    'phase2-round2-update', 'phase2-appointment-fix', 'phase2-failed-conversations',
    'phase2-remaining-failure', 'phase2-completion-update', 'phase2-independent-actions',
    'phase2-it-request-update', 'phase2-ob08-diagnostics', 'phase2-github',
    'onboarding-submission',
}
FILES = {'fix_phase2_quotes.py', 'publish_phase2.py'}
DATED = re.compile(r'^(?:phase2-(?:queue-results|final-reports)-\d{8}-\d{6}\.zip|'
                   r'phase2-(?:verification|publication)-\d{8}-\d{6}\.json|'
                   r'onboarding-before-rename-\d{8}-\d{6}-\d{6}\.zip|'
                   r'before-publish-\d{8}-\d{6}\.zip)$', re.I)


def is_link(path):
    info = path.lstat()
    return path.is_symlink() or bool(getattr(info, 'st_file_attributes', 0) & getattr(stat, 'FILE_ATTRIBUTE_REPARSE_POINT', 0))


def candidates(downloads):
    found = []
    for path in sorted(downloads.iterdir()):
        if is_link(path):
            continue
        name = path.name.lower()
        if path.is_file() and (name in FILES or DATED.fullmatch(name) or
                               (path.suffix.lower() == '.zip' and path.stem.lower() in PACKAGES)):
            found.append(path)
        elif path.is_dir() and name in PACKAGES and (path / 'apply_update.py').is_file():
            # An extracted installer may be archived; a repo, environment or linked tree may not.
            protected = False
            for base, dirs, files in os.walk(path, followlinks=False):
                if {'.git', '.venv', 'venv'} & set(dirs) or '.env' in files:
                    protected = True
                    break
                if any(is_link(Path(base) / part) for part in dirs + files):
                    protected = True
                    break
            if not protected:
                found.append(path)
    return found


def save_manifest(path, data):
    tmp = path.with_suffix('.tmp')
    tmp.write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8')
    tmp.replace(path)


def archive(downloads, paths):
    downloads = downloads.resolve()
    stamp = datetime.now().strftime('%Y%m%d-%H%M%S-%f')
    folder = downloads / 'CEREBRUM_Archive' / 'Phase2' / stamp
    for parent in [folder.parent.parent, folder.parent]:
        if parent.exists() and is_link(parent):
            raise ValueError('Archive parent is a link; no files moved.')
    folder.mkdir(parents=True, exist_ok=False)
    manifest = folder / 'manifest.json'
    data = {'format': 1, 'scope': 'Known Phase 2 downloads only',
            'files': [{'name': p.name, 'state': 'planned'} for p in paths]}
    save_manifest(manifest, data)
    allowed = set(candidates(downloads))
    for item, source in zip(data['files'], paths):
        if source.parent.resolve() != downloads or source not in allowed or is_link(source):
            raise ValueError(f'Not an eligible download: {source.name}')
        destination = folder / source.name
        if destination.exists():
            raise FileExistsError(destination)
        source.rename(destination)
        item['state'] = 'archived'
        save_manifest(manifest, data)
    return manifest


def restore(manifest):
    manifest = manifest.resolve()
    folder = manifest.parent
    if folder.parent.name != 'Phase2' or folder.parent.parent.name != 'CEREBRUM_Archive':
        raise ValueError('Use the manifest inside CEREBRUM_Archive/Phase2/<timestamp>.')
    downloads = folder.parent.parent.parent
    data = json.loads(manifest.read_text(encoding='utf-8'))
    if data.get('format') != 1:
        raise ValueError('Unknown manifest format')
    restored = 0
    for item in reversed(data['files']):
        name = item['name']
        if Path(name).name != name or name in ('.', '..') or '/' in name or '\\' in name:
            raise ValueError('Invalid filename in manifest')
        source, destination = folder / name, downloads / name
        if item['state'] == 'restored' or not source.exists():
            continue
        if destination.exists() or destination.is_symlink():
            raise FileExistsError(f'Will not overwrite {destination}; resolve the name collision before undoing.')
        if is_link(source):
            raise ValueError('Will not restore a linked entry')
        source.rename(destination)
        item['state'] = 'restored'
        save_manifest(manifest, data)
        restored += 1
    return restored


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--apply', action='store_true')
    mode.add_argument('--undo', type=Path)
    parser.add_argument('--downloads', type=Path, default=Path.home() / 'Downloads')
    args = parser.parse_args()
    if args.undo:
        print(f'Restored {restore(args.undo)} entries; no existing file was overwritten.')
        return
    downloads = args.downloads.resolve()
    if not downloads.is_dir():
        raise SystemExit(f'Downloads folder not found: {downloads}')
    selected = candidates(downloads)
    if not selected:
        print('No matching old Phase 2 downloads found. Nothing moved.')
        return
    print('Archive these known Phase 2 downloads:')
    for p in selected:
        print(f'  {p.name}')
    if not args.apply:
        print('Preview only. Use --apply to move them into CEREBRUM_Archive/Phase2.')
        return
    manifest = archive(downloads, selected)
    print(f'Archived {len(selected)} entries. Nothing deleted.')
    print(f'Undo manifest: {manifest}')
    print('Working repositories, Phase 3, mentor reviews, CVs and unrelated files were left in place.')


if __name__ == '__main__':
    main()
