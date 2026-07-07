"""
Vectorized transformers that shape a raw incoming trade JSON payload into
the numerical feature schema consumed by both the rules engine and the
gradient boosting model.
"""
from typing import Any, Dict


REQUIRED_FIELDS = [
    "trade_id",
    "india_vix",
    "cpra_grade",
    "historical_fail_rate",
    "trade_size_inr",
    "epi_flag",
    "peak_margin_utilization",
]


class MalformedTradePayload(ValueError):
    pass


def _validate(payload: Dict[str, Any]) -> None:
    missing = [f for f in REQUIRED_FIELDS if f not in payload]
    if missing:
        raise MalformedTradePayload(f"Missing required fields: {missing}")


def engineer_features(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate the raw trade payload and return the features as a dictionary.
    """
    _validate(payload)
    return payload
