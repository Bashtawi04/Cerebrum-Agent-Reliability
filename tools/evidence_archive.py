"""Portable, content-checked archives for evaluation evidence (standard library)."""
from pathlib import Path, PurePosixPath
import hashlib
import zipfile


def blob_id(data):
    return hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()


def read_archive(path, *, allow_windows_names=False):
    entries = {}
    with zipfile.ZipFile(path) as archive:
        for info in archive.infolist():
            if info.is_dir():
                continue
            name = info.filename
            if '\\' in name and not allow_windows_names:
                raise ValueError('Archive contains Windows separators')
            name = name.replace('\\', '/')
            parts = PurePosixPath(name)
            if parts.is_absolute() or '..' in parts.parts or ':' in name or name in entries:
                raise ValueError('Unsafe or duplicate evidence entry')
            entries[name] = archive.read(info)
    return entries


def write_archive(destination, entries):
    """Write forward-slash entry names; refuse replacement of an existing archive."""
    with zipfile.ZipFile(destination, 'x', compression=zipfile.ZIP_DEFLATED) as archive:
        for name, data in sorted(entries.items()):
            archive.writestr(PurePosixPath(name).as_posix(), data)


def archive_directory(source, destination):
    source = Path(source).resolve()
    destination = Path(destination).resolve()
    if source == destination or source in destination.parents:
        raise ValueError('Archive destination must be outside the evidence directory')
    entries = {p.relative_to(source).as_posix(): p.read_bytes()
               for p in sorted(source.rglob('*')) if p.is_file()}
    write_archive(destination, entries)


def verify_archive(path, manifest):
    if blob_id(Path(path).read_bytes()) != manifest['archive_git_blob_sha1']:
        raise ValueError('Evidence archive differs from its recorded fingerprint')
    entries = read_archive(path)
    actual = {name: blob_id(data) for name, data in entries.items()}
    if actual != manifest['files']:
        raise ValueError('Evidence member content differs from its recorded fingerprint')
    return entries
