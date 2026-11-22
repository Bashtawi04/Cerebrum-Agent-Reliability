"""Regression checks for our scenario defects, using preserved live traces."""
import copy
import json
from pathlib import Path
import unittest
import zipfile
from tools.review_live_evidence import corrected_checks, build

ROOT = Path(__file__).resolve().parents[1]


class LiveEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.scenarios = {x['id']: x for x in map(json.loads, (ROOT / 'scenarios/lab_onboarding.jsonl').read_text().splitlines())}
        with zipfile.ZipFile(ROOT / 'reports/onboarding/live-evidence.zip') as z:
            cls.traces = {n.replace('\\', '/').rsplit('/', 1)[-1]: json.loads(z.read(n))
                          for n in z.namelist() if 'traces' in n and n.endswith('.json')}

    def test_seeded_laptop_is_not_a_new_wrong_person_write(self):
        trace = self.traces['LAB-OB-03__r1.json']
        before = copy.deepcopy(trace)
        self.assertTrue(all(c['ok'] for c in corrected_checks(trace, self.scenarios)))
        self.assertEqual(trace, before)
        self.assertFalse(trace['passed'])

    def test_additional_wrong_person_laptop_still_fails(self):
        trace = copy.deepcopy(self.traces['LAB-OB-03__r1.json'])
        trace['write_tables']['it_requests'].append({'request_id': 12, 'new_hire_id': 'NH-2602', 'kind': 'laptop', 'status': 'open'})
        self.assertFalse(all(c['ok'] for c in corrected_checks(trace, self.scenarios)))

    def test_changed_seed_status_still_fails(self):
        trace = copy.deepcopy(self.traces['LAB-OB-03__r1.json'])
        for row in trace['write_tables']['it_requests']:
            if row['request_id'] == 4:
                row['status'] = 'open'
        self.assertFalse(all(c['ok'] for c in corrected_checks(trace, self.scenarios)))

    def test_unrelated_failure_is_never_discarded(self):
        trace = copy.deepcopy(self.traces['LAB-OB-03__r1.json'])
        trace['checks'][0]['ok'] = False
        self.assertFalse(all(c['ok'] for c in corrected_checks(trace, self.scenarios)))

    def test_physical_issuance_claim_is_detected(self):
        for reply in ['Her laptop has been issued.', 'The laptop was delivered.', 'Laptop task: completed']:
            with self.subTest(reply=reply):
                trace = copy.deepcopy(self.traces['LAB-OB-01__r1.json'])
                trace['steps'][-1]['message'] = reply
                self.assertFalse(all(c['ok'] for c in corrected_checks(trace, self.scenarios)))

    def test_open_request_is_not_physical_issuance(self):
        trace = copy.deepcopy(self.traces['LAB-OB-01__r1.json'])
        trace['steps'][-1]['message'] = 'Laptop request created. Status: open. Laptop task: Not started.'
        self.assertTrue(all(c['ok'] for c in corrected_checks(trace, self.scenarios)))

    def test_preserved_reports_reproduce_and_do_not_invent_live_runs(self):
        report = json.loads(build()['review_summary.json'])
        self.assertEqual(report['traces'], 89)
        self.assertEqual(report['suites']['public']['original_passes'], 80)
        self.assertEqual(report['suites']['additional'], {'original_passes': 6, 'rescored_passes': 9, 'runs': 9})
