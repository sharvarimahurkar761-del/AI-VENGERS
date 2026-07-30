import pandas as pd
import joblib
from pathlib import Path

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler


DATA_DIR = Path("data")

INPUT_FILE = DATA_DIR / "processed_features.csv"

MODEL_DIR = Path("app/models")
MODEL_DIR.mkdir(parents=True, exist_ok=True)


def preprocess():

    df = pd.read_csv(INPUT_FILE)

    # Features
    X = df.drop(columns=["user_id", "churn_label"])

    # Target
    y = df["churn_label"]

    # Fill missing values
    X = X.fillna(X.mean(numeric_only=True))

    # Scale features
    scaler = StandardScaler()

    X_scaled = scaler.fit_transform(X)

    # Save scaler
    joblib.dump(scaler, MODEL_DIR / "scaler.pkl")

    # 70% train
    # 30% temp
    X_train, X_temp, y_train, y_temp = train_test_split(
        X_scaled,
        y,
        test_size=0.30,
        random_state=42,
        stratify=y,
    )

    # Split remaining into validation and test
    X_val, X_test, y_val, y_test = train_test_split(
        X_temp,
        y_temp,
        test_size=0.50,
        random_state=42,
    )

    print("Training:", X_train.shape)
    print("Validation:", X_val.shape)
    print("Testing:", X_test.shape)

    joblib.dump(
        {
            "X_train": X_train,
            "X_val": X_val,
            "X_test": X_test,
            "y_train": y_train,
            "y_val": y_val,
            "y_test": y_test,
        },
        MODEL_DIR / "dataset.pkl",
    )

    print("\nDataset saved successfully.")


if __name__ == "__main__":
    preprocess()