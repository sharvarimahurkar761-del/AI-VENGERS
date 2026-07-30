from pydantic import BaseModel
from typing import List


class RiskRequest(BaseModel):
    usage_decline: float
    tickets_last30: int
    negative_sentiment: float
    feature_dropout: float
    active_days: int
    support_delay: float
    payment_delay: float


class Attribution(BaseModel):
    feature: str
    impact: float


class RiskResponse(BaseModel):
    risk_score: float
    attributions: List[Attribution]
    model_version: str