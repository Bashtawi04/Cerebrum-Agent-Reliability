"""Verify the optional cleanup cannot consume the active project or overwrite user files."""
import tempfile
from pathlib import Path
import unittest
from tools.organize_downloads import candidates, archive, restore


class CleanupTests(unittest.TestCase):
    def test_only_known_downloads_are_archived_and_restorable(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            old = root / 'phase2-appointment-fix.zip'
            old.write_bytes(b'old installer')
            for name in ['Yahya_CV.pdf', 'Yahya_Phase2_Review_Round2.pdf', 'Intern_2_Onboarding_Agent_ID32_Phase3.zip', 'unrelated.zip']:
                (root / name).write_bytes(b'keep')
            repo = root / 'yahya-onboarding-repo'
            repo.mkdir(); (repo / 'README.md').write_text('work')
            self.assertEqual(candidates(root), [old])
            manifest = archive(root, candidates(root))
            self.assertFalse(old.exists())
            self.assertEqual((repo / 'README.md').read_text(), 'work')
            self.assertEqual(restore(manifest), 1)
            self.assertEqual(old.read_bytes(), b'old installer')
            self.assertEqual(restore(manifest), 0)

    def test_undo_never_overwrites_a_new_download(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); old = root / 'fix_phase2_quotes.py'; old.write_text('old')
            manifest = archive(root, candidates(root))
            old.write_text('new')
            with self.assertRaises(FileExistsError):
                restore(manifest)
            self.assertEqual(old.read_text(), 'new')
            self.assertEqual((manifest.parent / old.name).read_text(), 'old')

    def test_extracted_folder_with_environment_is_preserved(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); folder = root / 'phase2-round2-update'; folder.mkdir()
            (folder / 'apply_update.py').write_text('installer')
            (folder / '.venv').mkdir()
            self.assertEqual(candidates(root), [])

    def test_unknown_paths_cannot_be_archived(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); unknown = root / 'important.txt'; unknown.write_text('keep')
            with self.assertRaises(ValueError):
                archive(root, [unknown])
            self.assertEqual(unknown.read_text(), 'keep')


if __name__ == '__main__':
    unittest.main()
