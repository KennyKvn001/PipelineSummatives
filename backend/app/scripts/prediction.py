from .model import dropout_model
from app.schema import StudentInput
import pandas as pd
from app.config import settings


class DropoutPredictor:
    def __init__(self):
        self.model_data = None
        self.load_model()

    def load_model(self):
        self.model_data = dropout_model.load_pretrained()

    def predict(self, student_data: StudentInput):
        """Make prediction for a single student"""
        input_df = pd.DataFrame([student_data.dict()])
        processed_input = self.model_data["preprocessor"].transform(input_df)
        proba = self.model_data["model"].predict_proba(processed_input)[0][0]

        return {
            "probability": float(proba),
            "risk_level": self._get_risk_level(proba),
            "model_version": "1.0",
        }

    def _get_risk_level(self, probability):
        if probability < 0.3:
            return "low"
        elif probability < 0.7:
            return "medium"
        return "high"
