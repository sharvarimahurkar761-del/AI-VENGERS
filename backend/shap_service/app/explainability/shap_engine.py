import numpy as np
import joblib
import shap
import torch
import matplotlib.pyplot as plt

from pathlib import Path
from app.models.model import RiskPredictionModel

MODEL_DIR = Path(__file__).resolve().parent.parent / "models"

FEATURE_NAMES = [
    "usage_decline",
    "tickets_last30",
    "negative_sentiment",
    "feature_dropout",
    "active_days",
    "support_delay",
    "payment_delay"
]

# Load processed dataset
dataset = joblib.load(MODEL_DIR / "dataset.pkl")
X_train = torch.FloatTensor(dataset["X_train"])

# Load trained model
model = RiskPredictionModel(X_train.shape[1])
model.load_state_dict(
    torch.load(
        MODEL_DIR / "risk_model.pth",
        map_location=torch.device("cpu")
    )
)
model.eval()

# Background samples for SHAP
background = X_train[:5]

# Use GradientExplainer as DeepExplainer has a known PyTorch size mismatch bug during shap_values()
explainer = shap.GradientExplainer(model, background)


def explain_customer(customer_features):
    """
    Returns:
    {
        risk_score: float,
        attributions: [...]
    }
    """

    customer_np = np.asarray(
        customer_features, dtype=np.float32).reshape(1, -1)
    customer = torch.FloatTensor(customer_np)

    with torch.no_grad():
        risk_score = float(model(customer).item())

    shap_values = explainer.shap_values(customer)

    # Handle list output
    if isinstance(shap_values, list):
        shap_values = shap_values[0]

    shap_values = np.asarray(shap_values)

    # Normalize shape to (7,)
    while shap_values.ndim > 1:
        shap_values = shap_values[0]

    attributions = []

    for feature, impact in zip(FEATURE_NAMES, shap_values):
        attributions.append({
            "feature": feature,
            "impact": round(float(impact), 4)
        })

    return {
        "risk_score": round(risk_score, 4),
        "attributions": attributions
    }


if __name__ == "__main__":

    sample = dataset["X_test"][0]

    result = explain_customer(sample)

    print("\n===== Risk Prediction =====")
    print("Risk Score:", result["risk_score"])

    print("\n===== SHAP Attributions =====")
    for item in result["attributions"]:
        print(f"{item['feature']:20s}: {item['impact']}")

    # Generate SHAP Bar Plot
    customer = torch.FloatTensor(
        np.asarray(sample, dtype=np.float32).reshape(1, -1)
    )

    shap_values = explainer.shap_values(customer)

    if isinstance(shap_values, list):
        shap_values = shap_values[0]

    shap_values = np.asarray(shap_values)

    while shap_values.ndim > 1:
        shap_values = shap_values[0]

    explanation = shap.Explanation(
        values=shap_values,
        data=sample,
        feature_names=FEATURE_NAMES
    )

    shap.plots.bar(explanation, show=False)

    plt.tight_layout()
    plt.savefig("data/shap_bar.png")
    plt.close()

    print("\nSHAP bar plot saved as data/shap_bar.png")
