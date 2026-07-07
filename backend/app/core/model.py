"""
Loads the pickled Gradient Boosting Pipeline and exposes a non-blocking
inference method. Scikit-learn's `.predict_proba` is CPU-bound and blocking,
so it must never be awaited directly on the asyncio event loop - callers use
`run_in_threadpool` (see api/endpoints.py) to avoid starving concurrent
request handling.
"""
import pickle
import logging
from pathlib import Path
from typing import List

import pandas as pd

from app.config import settings

logger = logging.getLogger("risk_engine.model")


class RiskModel:
    def __init__(self, model_path: str):
        self.model_path = Path(model_path)
        self.model = None
        self.expected_auc = settings.MODEL_EXPECTED_AUC
        self._load()

    def _load(self):
        if not self.model_path.exists():
            logger.warning(f"Model artifact not found at {self.model_path}.")
            return
        with open(self.model_path, "rb") as f:
            self.model = pickle.load(f)
        logger.info("Loaded gradient boosting pipeline from %s", self.model_path)

    def predict_proba(self, features: dict) -> float:
        """
        Blocking call. Must be invoked via run_in_threadpool from async code.
        Returns probability of settlement failure (positive class).
        """
        if not self.model:
            return 0.0

        # The Pipeline expects a DataFrame
        df = pd.DataFrame([features])
        proba = self.model.predict_proba(df)[0][1]
        return float(proba)

    def batch_predict_proba(self, feature_rows: List[dict]) -> List[float]:
        if not self.model:
            return [0.0] * len(feature_rows)
            
        df = pd.DataFrame(feature_rows)
        probas = self.model.predict_proba(df)[:, 1]
        return [float(p) for p in probas]


_model_instance: RiskModel | None = None


def get_model() -> RiskModel:
    global _model_instance
    if _model_instance is None:
        _model_instance = RiskModel(settings.MODEL_PATH)
    return _model_instance
