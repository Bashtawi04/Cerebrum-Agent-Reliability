"""Tests for lab/gate.py. They are the specification: make them pass without editing them."""
import unittest

from lab.gate import compare
from lab.models import ScenarioSummary
from lab.stats import wilson_interval


def summ(sid, passes, runs, safety=()):
    low, high = wilson_interval(passes, runs)
    return ScenarioSummary(sid, 1, runs, passes, low, high, None, "x", [], list(safety))


class GateTests(unittest.TestCase):
    def test_same_results_pass(self):
        base = [summ("A", 10, 10), summ("B", 7, 10)]
        result = compare(base, [summ("A", 10, 10), summ("B", 7, 10)])
        self.assertTrue(result.ok)
        self.assertEqual(result.reasons, [])

    def test_noise_is_not_a_regression(self):
        self.assertTrue(compare([summ("A", 10, 10)], [summ("A", 6, 10)]).ok)   # intervals still overlap

    def test_big_drop_is_a_regression(self):
        result = compare([summ("A", 10, 10)], [summ("A", 4, 10)])
        self.assertFalse(result.ok)
        self.assertEqual(result.reasons, ["regression: A 10/10 now 4/10"])

    def test_missing_scenario(self):
        result = compare([summ("A", 10, 10), summ("B", 10, 10)], [summ("A", 10, 10)])
        self.assertEqual(result.reasons, ["missing: B"])

    def test_new_scenario_is_fine(self):
        self.assertTrue(compare([summ("A", 10, 10)], [summ("A", 10, 10), summ("N", 0, 3)]).ok)

    def test_safety_always_fails_and_comes_first(self):
        result = compare([summ("A", 10, 10), summ("B", 10, 10)],
                         [summ("A", 1, 10), summ("B", 10, 10, ["write_before_approval", "fabricated_approval"])])
        self.assertFalse(result.ok)
        self.assertEqual(result.reasons, ["safety: B write_before_approval, fabricated_approval", "regression: A 10/10 now 1/10"])


if __name__ == "__main__":
    unittest.main()
