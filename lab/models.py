"""Plain data classes shared by the lab modules. Given to you complete; you do not need to change this file."""
from dataclasses import dataclass, field


@dataclass
class ScenarioSummary:
    id: str
    level: int
    runs: int                 # how many times the scenario was run (all result files together)
    passes: int               # how many of those runs passed
    low: float                # lower end of the 95% Wilson interval for the true pass rate
    high: float               # upper end
    pass_hat_3: float | None  # estimated chance that 3 runs in a row all pass; None when there are fewer than 3 runs
    label: str                # "failing", "flaky", "unproven" or "solid" (see summarise)
    top_failures: list[tuple[str, int]] = field(default_factory=list)  # (check name, count), at most 3
    safety: list[str] = field(default_factory=list)                     # distinct violation kinds seen in any run


@dataclass
class Finding:
    rule: str       # "claims_done_without_write", "denies_change_but_wrote" or "claims_proposal_without_request"
    step: int       # index of the step (0-based) in the trace whose reply contains the claim
    sentence: str   # the sentence that was flagged, after the cleaning described in lab/honesty.py (straight apostrophes, no * or backticks, no list mark)


@dataclass
class GateResult:
    ok: bool
    reasons: list[str] = field(default_factory=list)   # empty when ok; each reason starts with its rule name and a colon
