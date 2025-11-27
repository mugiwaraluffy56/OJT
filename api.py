from fastapi import FastAPI
from pydantic import BaseModel
from license_detector.models.soul_reader import SoulReader
import uvicorn
import os

app = FastAPI(
    title="AI License Soul-Reader™ API",
    description="An API for detecting software licenses from text.",
    version="1.0.0",
)

# Load the fine-tuned model
model_path = "fine-tuned-model"
if not os.path.exists(model_path):
    raise RuntimeError(f"Fine-tuned model not found at '{model_path}'. Please run `python3 train.py` first.")

soul_reader = SoulReader.from_pretrained(model_path)

class LicenseRequest(BaseModel):
    text: str

class LicenseResponse(BaseModel):
    predicted_license: str

@app.post("/predict", response_model=LicenseResponse)
def predict_license(request: LicenseRequest):
    """
    Predicts the license for a given text.
    """
    predicted_license = soul_reader.predict(request.text)
    return {"predicted_license": predicted_license}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
