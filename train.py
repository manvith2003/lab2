import pandas as pd
import json
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.pipeline import Pipeline
import os

# Load dataset
df = pd.read_csv("data/winequality-red.csv", sep=";")

X = df.drop("quality", axis=1)
y = df["quality"]

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Model pipeline
model = Pipeline([
    ("scaler", StandardScaler()),
    ("ridge", Ridge(alpha=0.5))
])

# Train
model.fit(X_train, y_train)

# Predict
y_pred = model.predict(X_test)

# Metrics
mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print(f"MSE: {mse}")
print(f"R2 Score: {r2}")

# Save outputs
os.makedirs("outputs", exist_ok=True)

joblib.dump(model, "outputs/model.pkl")

results = {
    "MSE": mse,
    "R2": r2
}

with open("outputs/results.json", "w") as f:
    json.dump(results, f, indent=4)

# Write metrics to GitHub Actions Job Summary
github_summary = os.getenv("GITHUB_STEP_SUMMARY")

if github_summary:
    with open(github_summary, "a") as f:
        f.write("## Experiment Results\n")
        f.write("**Name:** Manvith M  \n")
        f.write("**Roll No:** 2022BCS0066  \n\n")
        f.write(f"- **MSE:** {mse}\n")
        f.write(f"- **R2 Score:** {r2}\n")
