from fastapi import FastAPI
import joblib

app = FastAPI()

model = joblib.load("model.pkl")

@app.post("/predict")
def predict(features: list):
    pred = model.predict([features])[0]

    return {
        "name": "Manvith M",
        "roll_no": "2022BCS0066",
        "wine_quality": int(round(pred))
    }
