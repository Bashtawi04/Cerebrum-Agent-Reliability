"""Tests for lab/aggregate.py. They are the specification: make them pass without editing them."""
import unittest

from lab.aggregate import render_markdown, summarise
from lab.models import ScenarioSummary


def run(passed, failing=(), violations=()):
    return {"id": "x", "passed": passed, "violations": list(violations),
            "checks": [{"name": n, "ok": False, "detail": ""} for n in failing] + [{"name": "final_status", "ok": True, "detail": ""}]}


def entry(sid, level, passes, runs, details, violations=()):
    return {"id": sid, "level": level, "title": "t", "passes": passes, "runs": runs,
            "violations": list(violations), "detail": details}


FILE_A = [
    entry("S-01", 1, 3, 3, [run(True)] * 3),
    entry("S-02", 3, 2, 3, [run(True), run(False, ["approval requests"]), run(True)]),
    entry("S-03", 2, 0, 3, [run(False, ["effect a", "approval requests"]), run(False, ["effect a"]), run(False, ["effect a"])]),
]
FILE_B = [
    entry("S-02", 3, 5, 6, [run(True)] * 5 + [run(False, ["reply mentions 'booked'"])]),
    entry("S-04", 2, 3, 3, [run(True)] * 3, violations=["write_before_approval"]),
]


class SummariseTests(unittest.TestCase):
    def setUp(self):
        self.s = {x.id: x for x in summarise([FILE_A, FILE_B])}

    def test_one_summary_per_scenario_in_first_seen_order(self):
        self.assertEqual([x.id for x in summarise([FILE_A, FILE_B])], ["S-01", "S-02", "S-03", "S-04"])

    def test_counts_are_added_across_files(self):
        self.assertEqual((self.s["S-02"].runs, self.s["S-02"].passes, self.s["S-02"].level), (9, 7, 3))

    def test_interval_and_pass_hat(self):
        s = self.s["S-02"]
        self.assertAlmostEqual(s.low, 0.4526, places=3)
        self.assertAlmostEqual(s.high, 0.9368, places=3)
        self.assertAlmostEqual(s.pass_hat_3, 35 / 84)

    def test_pass_hat_is_none_below_three_runs(self):
        only = summarise([[entry("A", 1, 1, 2, [run(True), run(False)])]])
        self.assertIsNone(only[0].pass_hat_3)

    def test_labels(self):
        self.assertEqual(self.s["S-01"].label, "unproven")   # 3/3 is not enough runs to be called solid
        self.assertEqual(self.s["S-02"].label, "flaky")
        self.assertEqual(self.s["S-03"].label, "failing")
        many = summarise([[entry("A", 1, 12, 12, [run(True)] * 12)]])
        self.assertEqual(many[0].label, "solid")
        self.assertEqual(summarise([[entry("A", 1, 12, 12, [run(True)] * 12)]], solid_low=0.9)[0].label, "unproven")

    def test_top_failures(self):
        self.assertEqual(self.s["S-03"].top_failures, [("effect a", 3), ("approval requests", 1)])
        self.assertEqual(self.s["S-02"].top_failures, [("approval requests", 1), ("reply mentions 'booked'", 1)])
        self.assertEqual(self.s["S-01"].top_failures, [])

    def test_safety_is_collected(self):
        self.assertEqual(self.s["S-04"].safety, ["write_before_approval"])
        self.assertEqual(self.s["S-01"].safety, [])


class RenderTests(unittest.TestCase):
    def test_exact_table(self):
        rows = [ScenarioSummary("LRN-07", 3, 9, 7, 0.4526, 0.9368, 35 / 84, "flaky", [("approval requests", 2), ("effect a", 1)], []),
                ScenarioSummary("LRN-01", 1, 2, 2, 0.34, 1.0, None, "unproven", [], ["write_after_reject", "fabricated_approval"])]
        text = render_markdown(rows, "Own agent")
        lines = text.split("\n")
        self.assertEqual(lines[0], "## Own agent")
        self.assertEqual(lines[1], "")
        self.assertEqual(lines[2], "| scenario | level | passed | 95% interval | pass^3 | label | most common failing checks |")
        self.assertEqual(lines[3], "|---|---|---|---|---|---|---|")
        self.assertEqual(lines[4], "| LRN-07 | 3 | 7/9 | 0.45-0.94 | 0.42 | flaky | approval requests (2); effect a (1) |")
        self.assertEqual(lines[5], "| LRN-01 | 1 | 2/2 | 0.34-1.00 | n/a | unproven | - |")
        self.assertEqual(lines[6], "")
        self.assertEqual(lines[7], "2 scenarios, 11 runs, 9 passed. Safety: fabricated_approval, write_after_reject")

    def test_no_safety_says_none(self):
        text = render_markdown([ScenarioSummary("A", 1, 4, 4, 0.5, 1.0, 1.0, "unproven", [], [])])
        self.assertTrue(text.endswith("1 scenarios, 4 runs, 4 passed. Safety: none"))
        self.assertTrue(text.startswith("## Results"))


if __name__ == "__main__":
    unittest.main()
