import logging
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Depends
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.config import settings
from app.core.model import get_model
from app.core.rules import evaluate_hard_rules, has_hard_breach
from app.utils.processors import engineer_features, MalformedTradePayload
from app.api.websockets import manager
from app.db.database import get_db
from app.db.models import TradeEvaluation

logger = logging.getLogger("risk_engine.endpoints")
router = APIRouter(prefix=settings.API_V1_PREFIX)


class TradePayload(BaseModel):
    trade_id: str
    india_vix: float = Field(..., ge=0)
    cpra_grade: str
    historical_fail_rate: float = Field(..., ge=0, le=1)
    trade_size_inr: float = Field(..., ge=0)
    epi_flag: int = Field(..., ge=0, le=1)
    peak_margin_utilization: float = Field(..., ge=0)


class RiskAssessmentResponse(BaseModel):
    assessment_id: str
    trade_id: str
    risk_score: float
    is_high_risk: bool
    hard_rule_breach: bool
    violations: list
    evaluated_at: str
    trade_details: dict


@router.post("/trades/evaluate", response_model=RiskAssessmentResponse)
async def evaluate_trade(payload: TradePayload, db: Session = Depends(get_db)):
    try:
        features = engineer_features(payload.model_dump())
    except MalformedTradePayload as exc:
        raise HTTPException(status_code=422, detail=str(exc))

    violations = evaluate_hard_rules(features)
    hard_breach = has_hard_breach(violations)

    # Run blocking sklearn inference off the event loop.
    model = get_model()
    risk_score = await run_in_threadpool(model.predict_proba, features)

    is_high_risk = hard_breach or risk_score >= settings.HIGH_RISK_PROBABILITY_THRESHOLD

    evaluated_at_dt = datetime.now(timezone.utc)
    
    response = RiskAssessmentResponse(
        assessment_id=str(uuid.uuid4()),
        trade_id=payload.trade_id,
        risk_score=round(risk_score, 4),
        is_high_risk=is_high_risk,
        hard_rule_breach=hard_breach,
        violations=[v.__dict__ for v in violations],
        evaluated_at=evaluated_at_dt.isoformat(),
        trade_details=payload.model_dump(),
    )

    # Save to database
    db_eval = TradeEvaluation(
        assessment_id=response.assessment_id,
        trade_id=response.trade_id,
        risk_score=response.risk_score,
        is_high_risk=response.is_high_risk,
        hard_rule_breach=response.hard_rule_breach,
        violations=response.violations,
        trade_details=response.trade_details,
        evaluated_at=evaluated_at_dt.replace(tzinfo=None) # store as naive UTC for Postgres
    )
    db.add(db_eval)
    db.commit()

    if is_high_risk:
        await manager.broadcast(
            {
                "type": "RISK_ALERT",
                "data": response.model_dump(),
            }
        )
        logger.warning("High-risk trade flagged: %s (score=%.4f)", payload.trade_id, risk_score)

    return response


@router.get("/trades/history")
async def get_history(limit: int = 50, db: Session = Depends(get_db)):
    """Fetch recent high-risk trades to populate the dashboard on load."""
    evals = db.query(TradeEvaluation).filter(TradeEvaluation.is_high_risk == True).order_by(TradeEvaluation.evaluated_at.desc()).limit(limit).all()
    results = []
    for e in evals:
        results.append({
            "assessment_id": e.assessment_id,
            "trade_id": e.trade_id,
            "risk_score": e.risk_score,
            "is_high_risk": e.is_high_risk,
            "hard_rule_breach": e.hard_rule_breach,
            "violations": e.violations,
            "trade_details": e.trade_details,
            "evaluated_at": e.evaluated_at.isoformat() + "Z" if e.evaluated_at else None
        })
    return results


@router.get("/health")
async def health_check():
    model = get_model()
    return {
        "status": "ok",
        "model_loaded": model.model is not None,
        "expected_auc": model.expected_auc,
    }
