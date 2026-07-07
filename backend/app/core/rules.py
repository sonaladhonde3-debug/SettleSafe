"""
Deterministic, hardcoded boolean rule engine.

These checks run BEFORE the ML model and are cheap/instant. Any hard breach
here short-circuits evaluation and is flagged regardless of what the model
predicts, since these represent bright-line operational/compliance limits.
"""
from dataclasses import dataclass
from typing import List


@dataclass
class RuleViolation:
    code: str
    message: str
    severity: str  # "HARD" or "SOFT"


def evaluate_hard_rules(trade: dict) -> List[RuleViolation]:
    """
    Evaluate a single trade payload against deterministic margin/settlement
    boundaries.
    """
    violations: List[RuleViolation] = []

    peak_margin = trade.get("peak_margin_utilization", 0.0)
    if peak_margin >= 1.0:
        violations.append(
            RuleViolation(
                code="MARGIN_BREACH",
                message=f"Peak margin utilization {peak_margin:.2f} exceeds hard limit 1.0.",
                severity="HARD",
            )
        )

    india_vix = trade.get("india_vix", 0.0)
    cpra_grade = trade.get("cpra_grade", "")
    if cpra_grade == "CPRA_4" and india_vix > 35.0:
        violations.append(
            RuleViolation(
                code="EXTREME_VOLATILITY_CPRA4",
                message=f"High risk counterparty (CPRA_4) trading during extreme volatility (VIX: {india_vix:.2f}).",
                severity="HARD",
            )
        )

    hist_fail_rate = trade.get("historical_fail_rate", 0.0)
    if hist_fail_rate > 0.1:
        violations.append(
            RuleViolation(
                code="ELEVATED_FAIL_RATE",
                message=f"Counterparty historical fail rate is elevated ({hist_fail_rate:.2%}).",
                severity="SOFT",
            )
        )

    return violations


def has_hard_breach(violations: List[RuleViolation]) -> bool:
    return any(v.severity == "HARD" for v in violations)
