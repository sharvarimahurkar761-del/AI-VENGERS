import joblib
import torch
import torch.nn as nn
import torch.optim as optim

from pathlib import Path

from app.models.model import RiskPredictionModel

MODEL_DIR = Path("app/models")

# Load dataset
dataset = joblib.load(MODEL_DIR / "dataset.pkl")

X_train = torch.FloatTensor(dataset["X_train"])
y_train = torch.FloatTensor(dataset["y_train"].values).view(-1, 1)

X_val = torch.FloatTensor(dataset["X_val"])
y_val = torch.FloatTensor(dataset["y_val"].values).view(-1, 1)

input_size = X_train.shape[1]

model = RiskPredictionModel(input_size)

criterion = nn.BCELoss()

optimizer = optim.Adam(
    model.parameters(),
    lr=0.001
)

epochs = 100

for epoch in range(epochs):

    model.train()

    outputs = model(X_train)

    loss = criterion(outputs, y_train)

    optimizer.zero_grad()

    loss.backward()

    optimizer.step()

    model.eval()

    with torch.no_grad():

        val_outputs = model(X_val)

        val_loss = criterion(val_outputs, y_val)

    if (epoch + 1) % 10 == 0:

        print(
            f"Epoch {epoch+1}/{epochs} | "
            f"Train Loss: {loss.item():.4f} | "
            f"Validation Loss: {val_loss.item():.4f}"
        )

torch.save(
    model.state_dict(),
    MODEL_DIR / "risk_model.pth"
)

print("\nModel saved successfully!")
