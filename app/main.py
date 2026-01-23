from fastapi import FastAPI
from pydantic import BaseModel
import joblib

app = FastAPI()

# Load trained model
model = joblib.load("model.pkl")

# Define request schema
class WineFeatures(BaseModel):
    features: list[float]

@app.post("/predict")
def predict(data: WineFeatures):
    pred = model.predict([data.features])[0]

    return {
        "name": "Manvith",
        "roll_no": "2022BCS0066",
        "wine_quality": int(round(pred))
    }
