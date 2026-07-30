import joblib

data = joblib.load("app/models/dataset.pkl")

print("Training Features:", data["X_train"].shape)
print("Training Labels:", data["y_train"].shape)

print("\nSample:")
print(data["X_train"][:3])