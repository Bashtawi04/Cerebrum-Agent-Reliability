"""Portable Onboarding evidence and exact scenario snapshots."""
import json
from pathlib import Path
import tempfile
import unittest
import zipfile
from tools.evidence_archive import archive_directory, verify_archive
from tools.evaluate_onboarding import snapshot_scenarios, git_blob_id
ROOT = Path(__file__).resolve().parents[1]


class ArchiveAndSnapshotTests(unittest.TestCase):
    def test_nested_archive_extracts_to_directories_with_identical_bytes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / 'batch'
            (source / 'traces').mkdir(parents=True)
            content = b'{"message": "unchanged"}\r\n'
            (source / 'traces/case.json').write_bytes(content)
            target = root / 'batch.zip'
            archive_directory(source, target)
            with zipfile.ZipFile(target) as archive:
                self.assertEqual(archive.namelist(), ['traces/case.json'])
                archive.extractall(root / 'extracted')
            self.assertEqual((root / 'extracted/traces/case.json').read_bytes(), content)
            with self.assertRaises(FileExistsError):
                archive_directory(source, target)

    def test_normalized_onboarding_archive_has_all_original_member_hashes(self):
        folder = ROOT / 'reports/onboarding'
        entries = verify_archive(folder / 'live-evidence.zip', json.loads((folder / 'archive_manifest.json').read_text()))
        self.assertEqual(len(entries), 95)
        self.assertFalse(any('\\' in name for name in entries))

    def test_scenario_snapshot_is_exact_and_independent_of_later_source_edits(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / 'input.jsonl'
            source.write_bytes(b'{"id":"test","pattern":"a\\\\sb"}\r\n')
            out = root / 'evidence'
            out.mkdir()
            snapshot = snapshot_scenarios(source, out)
            original_hash = git_blob_id(source)
            self.assertEqual(snapshot.read_bytes(), source.read_bytes())
            source.write_text('changed')
            self.assertEqual(git_blob_id(snapshot), original_hash)
            with self.assertRaises(FileExistsError):
                snapshot_scenarios(source, out)
