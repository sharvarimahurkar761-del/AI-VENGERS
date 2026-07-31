from fastapi import APIRouter
from datetime import datetime
import pandas as pd
from pathlib import Path

from app.api.schemas import RiskRequest

from app.explainability.shap_engine import explain_customer

router = APIRouter()

FEEDBACK_FILE = Path("feedback.csv")


@router.get("/")
def home():
    return {
        "message": "PulseIQ Risk Engine Running 🚀"
    }


@router.post("/risk/score")
def risk_score(request: RiskRequest):

    features = [
        request.usage_decline,
        request.tickets_last30,
        request.negative_sentiment,
        request.feature_dropout,
        request.active_days,
        request.support_delay,
        request.payment_delay
    ]

    result = explain_customer(features)

    return {
        "risk_score": result["risk_score"],
        "attributions": result["attributions"],
        "model_version": "v1.0",
        "timestamp": datetime.now().isoformat()
    }


@router.post("/feedback")
def feedback(data: dict):

    df = pd.DataFrame([data])

    if FEEDBACK_FILE.exists():
        df.to_csv(FEEDBACK_FILE, mode="a", header=False, index=False)
    else:
        df.to_csv(FEEDBACK_FILE, index=False)

    return {
        "message": "Feedback stored successfully."
    }
