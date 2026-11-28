"""Small statistics for judging an agent from repeated runs. Standard library only."""
from math import comb, isfinite, sqrt


_NO_K = object()


def _counts(passes: int, runs: int, k: object = _NO_K) -> None:
    if type(passes) is not int or type(runs) is not int or runs < 1 or not 0 <= passes <= runs:
        raise ValueError('passes and runs must be integers with 0 <= passes <= runs and runs >= 1')
    if k is not _NO_K and (type(k) is not int or not 1 <= k <= runs):
        raise ValueError('k must be an integer between 1 and runs')


def _z_score(z: float) -> None:
    if not isinstance(z, (int, float)) or isinstance(z, bool) or not isfinite(z) or z <= 0:
        raise ValueError('z must be finite and positive')

def wilson_interval(passes: int, runs: int, z: float=1.96) -> tuple[float, float]:
    """The 95% Wilson score interval for the true pass rate, from `passes` successes in `runs` trials.

    With p = passes / runs:
        centre = (p + z^2 / (2 * runs)) / (1 + z^2 / runs)
        half   = z * sqrt(p * (1 - p) / runs + z^2 / (4 * runs^2)) / (1 + z^2 / runs)
    Return (centre - half, centre + half), each limited to the range 0..1.
    Raise ValueError when runs < 1 or passes is not between 0 and runs.
    """
    _counts(passes, runs)
    _z_score(z)
    p = passes / runs
    denominator = 1 + z * z / runs
    centre = (p + z * z / (2 * runs)) / denominator
    half = z * sqrt(p * (1 - p) / runs + z * z / (4 * runs * runs)) / denominator
    return (0.0 if passes == 0 else max(0.0, centre - half),
            1.0 if passes == runs else min(1.0, centre + half))

def pass_hat_k(passes: int, runs: int, k: int) -> float:
    """The chance that k runs, picked at random from these `runs`, ALL pass (the "pass^k" idea).

    It is comb(passes, k) / comb(runs, k). It is 0 when passes < k.
    Raise ValueError when the arguments are invalid or k < 1 or k > runs.
    """
    _counts(passes, runs, k)
    return comb(passes, k) / comb(runs, k) if passes >= k else 0.0

def pass_at_k(passes: int, runs: int, k: int) -> float:
    """The chance that at least ONE of k runs, picked at random from these `runs`, passes (the "pass@k" idea).

    It is 1 - comb(runs - passes, k) / comb(runs, k). Same errors as pass_hat_k.
    """
    _counts(passes, runs, k)
    failures = runs - passes
    return 1 - comb(failures, k) / comb(runs, k) if failures >= k else 1.0

def runs_for_lower_bound(target: float, z: float=1.96) -> int:
    """The smallest number of runs n such that n passes out of n gives a Wilson lower bound of at least `target`.

    Example: how many perfect runs before you may say "the true pass rate is at least 80%"?
    Raise ValueError unless 0 < target < 1. Stop looking at 100000 runs and raise ValueError.
    """
    _z_score(z)
    if not isinstance(target, (int, float)) or isinstance(target, bool) or not isfinite(target) or not 0 < target < 1:
        raise ValueError('target must be between 0 and 1')
    for n in range(1, 100001):
        if wilson_interval(n, n, z)[0] >= target:
            return n
    raise ValueError('target needs more than 100000 perfect runs')
