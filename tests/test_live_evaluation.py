"""The live-run wrapper must preserve and honestly report failing evidence."""
import shlex
import unittest
from tools.evaluate_onboarding import agent_command, inspect_results


class EvaluationEvidenceTests(unittest.TestCase):
    def test_failed_run_is_not_hidden_by_harness_success(self):
        row = {'id': 'X', 'runs': 2, 'passes': 1, 'violations': [],
               'detail': [{'passed': True}, {'passed': False}]}
        self.assertFalse(inspect_results([row], ['X'], 2))

    def test_safety_and_missing_evidence_are_rejected(self):
        row = {'id': 'X', 'runs': 1, 'passes': 1, 'violations': [],
               'detail': [{'passed': True, 'violations': ['fabricated_approval']}]}
        self.assertFalse(inspect_results([row], ['X'], 1))
        with self.assertRaises(ValueError):
            inspect_results([row], ['X'], 2)
        with self.assertRaises(ValueError):
            inspect_results([row, row], ['X'], 1)
        row['passes'] = 0
        with self.assertRaises(ValueError):
            inspect_results([row], ['X'], 1)

    def test_windows_path_with_spaces_survives_harness_parser(self):
        path = 'C:/Users/Yahya Name/project/.venv/Scripts/python.exe'
        self.assertEqual(shlex.split(agent_command(path)), [path, '-X', 'utf8', 'agent_cli.py'])
