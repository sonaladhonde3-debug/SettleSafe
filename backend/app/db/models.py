from sqlalchemy import Column, Integer, String, Float, Boolean, JSON, DateTime
from datetime import datetime, timezone
from app.db.database import Base

class TradeEvaluation(Base):
    __tablename__ = "trade_evaluations"

    id = Column(Integer, primary_key=True, index=True)
    assessment_id = Column(String, unique=True, index=True)
    trade_id = Column(String, index=True)
    risk_score = Column(Float)
    is_high_risk = Column(Boolean)
    hard_rule_breach = Column(Boolean)
    violations = Column(JSON)
    trade_details = Column(JSON)
    evaluated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
