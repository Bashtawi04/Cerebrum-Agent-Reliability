"""Tests for lab/stats.py. They are the specification: make them pass without editing them."""
import unittest

from lab.stats import pass_at_k, pass_hat_k, runs_for_lower_bound, wilson_interval


class WilsonTests(unittest.TestCase):
    def assertInterval(self, got, low, high):
        self.assertAlmostEqual(got[0], low, places=3)
        self.assertAlmostEqual(got[1], high, places=3)

    def test_known_values(self):
        self.assertInterval(wilson_interval(7, 9), 0.4526, 0.9368)
        self.assertInterval(wilson_interval(5, 10), 0.2366, 0.7634)
        self.assertInterval(wilson_interval(8, 10), 0.4902, 0.9433)

    def test_all_pass_is_not_proof(self):
        low, high = wilson_interval(3, 3)
        self.assertAlmostEqual(low, 0.4385, places=3)   # three perfect runs only show "at least 44%"
        self.assertEqual(high, 1.0)
        self.assertAlmostEqual(wilson_interval(10, 10)[0], 0.7225, places=3)

    def test_no_pass(self):
        low, high = wilson_interval(0, 10)
        self.assertEqual(low, 0.0)
        self.assertAlmostEqual(high, 0.2775, places=3)

    def test_wider_with_fewer_runs(self):
        a, b = wilson_interval(5, 10), wilson_interval(50, 100)
        self.assertGreater(a[1] - a[0], b[1] - b[0])

    def test_bad_input(self):
        for args in [(1, 0), (-1, 5), (6, 5)]:
            with self.assertRaises(ValueError):
                wilson_interval(*args)


class PassKTests(unittest.TestCase):
    def test_pass_hat_k(self):
        self.assertAlmostEqual(pass_hat_k(7, 9, 3), 35 / 84)
        self.assertEqual(pass_hat_k(9, 9, 3), 1.0)
        self.assertEqual(pass_hat_k(2, 9, 3), 0.0)      # fewer passes than k: can never get k in a row
        self.assertEqual(pass_hat_k(7, 9, 1), 7 / 9)

    def test_pass_at_k(self):
        self.assertAlmostEqual(pass_at_k(5, 10, 2), 1 - 10 / 45)
        self.assertEqual(pass_at_k(7, 9, 3), 1.0)       # three tries, only two failures exist: one must pass
        self.assertEqual(pass_at_k(0, 9, 3), 0.0)

    def test_k_larger_than_runs(self):
        with self.assertRaises(ValueError):
            pass_hat_k(2, 3, 4)
        with self.assertRaises(ValueError):
            pass_at_k(2, 3, 0)


class RunsNeededTests(unittest.TestCase):
    def test_values(self):
        self.assertEqual(runs_for_lower_bound(0.7), 9)
        self.assertEqual(runs_for_lower_bound(0.8), 16)
        self.assertEqual(runs_for_lower_bound(0.9), 35)

    def test_bad_target(self):
        for target in (0, 1, 1.5, -0.2):
            with self.assertRaises(ValueError):
                runs_for_lower_bound(target)


if __name__ == "__main__":
    unittest.main()
