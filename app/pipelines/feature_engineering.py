import pandas as pd
from pathlib import Path


DATA_DIR = Path("data")

RAW_DATA = DATA_DIR / "raw_customer_data.csv"
OUTPUT_DATA = DATA_DIR / "processed_features.csv"


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convert raw customer signals into ML features.
    """

    engineered = df.copy()

    # Usage decline (example calculation)
    engineered["usage_decline"] = (
        (150 - engineered["usage_minutes"]) / 150
    ).round(3)

    # Feature dropout
    engineered["feature_dropout"] = (
        (20 - engineered["feature_usage"]) / 20
    ).round(3)

    # Active days per week
    engineered["active_days"] = (
        7 - engineered["last_login_days"]
    ).clip(lower=0)

    # Negative sentiment
    engineered["negative_sentiment"] = (
        1 - engineered["sentiment_score"]
    ).round(3)

    engineered.rename(
        columns={
            "support_tickets": "tickets_last30",
            "response_delay_hours": "support_delay",
            "payment_delay_days": "payment_delay"
        },
        inplace=True,
    )

    columns = [
        "user_id",
        "usage_decline",
        "tickets_last30",
        "negative_sentiment",
        "feature_dropout",
        "active_days",
        "support_delay",
        "payment_delay",
        "churn_label"
    ]

    return engineered[columns]


def main():
    df = pd.read_csv(RAW_DATA)

    processed = engineer_features(df)

    processed.to_csv(OUTPUT_DATA, index=False)

    print(processed.head())
    print("\nProcessed dataset saved to:")
    print(OUTPUT_DATA)


if __name__ == "__main__":
    main()