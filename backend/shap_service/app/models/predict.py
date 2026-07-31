import joblib
import torch
import pandas as pd

from pathlib import Path
from app.models.model import RiskPredictionModel

MODEL_DIR = Path(__file__).resolve().parent

scaler = joblib.load(MODEL_DIR / "scaler.pkl")

INPUT_SIZE = 7

model = RiskPredictionModel(INPUT_SIZE)

model.load_state_dict(
    torch.load(
        MODEL_DIR / "risk_model.pth",
        map_location=torch.device("cpu")
    )
)

model.eval()


def predict_risk(customer_features):

    columns = [
        "usage_decline",
        "tickets_last30",
        "negative_sentiment",
        "feature_dropout",
        "active_days",
        "support_delay",
        "payment_delay"
    ]

    df = pd.DataFrame([customer_features], columns=columns)

    scaled = scaler.transform(df)

    tensor = torch.FloatTensor(scaled)

    with torch.no_grad():
        risk_score = model(tensor)

    return float(risk_score.item())


# Demo code (runs ONLY when this file is executed directly)
if __name__ == "__main__":

    sample_customer = [
        0.55,
        3,
        0.72,
        0.60,
        2,
        14,
        3
    ]

    score = predict_risk(sample_customer)

    print(f"Predicted Risk Score: {score:.4f}")
