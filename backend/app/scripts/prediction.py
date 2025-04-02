from .model import dropout_model
from app.schema import StudentInput
import pandas as pd
from app.config import settings
import logging
import numpy as np


logger = logging.getLogger(__name__)


class DropoutPredictor:
    def __init__(self):
        self.model_data = None
        self.load_model()

    def load_model(self):
        try:
            # Load the model
            loaded_model = dropout_model.load_pretrained()

            # Store in a consistent format
            self.model_data = {
                "model": loaded_model,
                "preprocessor": None,  # Initialize to None
            }

            # If load_pretrained returned a dictionary with more data
            if isinstance(loaded_model, dict) and "preprocessor" in loaded_model:
                self.model_data["preprocessor"] = loaded_model["preprocessor"]
                self.model_data["model"] = loaded_model["model"]

            return self.model_data
        except Exception as e:
            logging.error(f"Failed to load model: {str(e)}")
            return None

    def predict(self, student_data: StudentInput):
        """Make prediction for a single student"""
        if not self.model_data:
            self.load_model()

        if not self.model_data or not self.model_data.get("model"):
            raise ValueError("Model could not be loaded")

        input_df = pd.DataFrame([student_data.dict()])

        # Apply preprocessing if available
        if self.model_data.get("preprocessor"):
            processed_input = self.model_data["preprocessor"].transform(input_df)
        else:
            processed_input = input_df.values

        # Make prediction
        model = self.model_data["model"]

        try:
            logging.info(f"Received prediction request with data: {student_data}")
            # Check if model is loaded
            if not self.model_data:
                self.load_model()
                if not self.model_data:
                    raise ValueError("Model could not be loaded")

            # Convert input to DataFrame and ensure all values are numeric
            input_dict = student_data.dict()

            # Explicitly convert values to ensure they're numeric
            for key in input_dict:
                if key == "Gender":
                    # Handle Gender specially if it's a string
                    if isinstance(input_dict[key], str):
                        input_dict[key] = 1 if input_dict[key].lower() == "male" else 0
                else:
                    # Ensure all other values are float
                    try:
                        input_dict[key] = float(input_dict[key])
                    except (ValueError, TypeError):
                        raise ValueError(
                            f"Field '{key}' has an invalid value: {input_dict[key]}"
                        )

            # Create DataFrame with the processed values
            input_df = pd.DataFrame([input_dict])

            # Print DataFrame info for debugging
            print("Input DataFrame data types:")
            print(input_df.dtypes)

            # Apply preprocessing if available
            if self.model_data.get("preprocessor"):
                processed_input = self.model_data["preprocessor"].transform(input_df)
            else:
                processed_input = input_df.values

            # Make prediction
            model = self.model_data["model"]

            # For TensorFlow/Keras models
            prediction = model.predict(processed_input)

            # Handle different output shapes
            if isinstance(prediction, np.ndarray):
                if len(prediction.shape) == 2:
                    proba = float(prediction[0][0])
                else:
                    proba = float(prediction[0])
            else:
                proba = float(
                    prediction.numpy()[0]
                    if hasattr(prediction, "numpy")
                    else prediction[0]
                )

            return {
                "dropout_probability": proba,
                "risk_level": self._get_risk_level(proba),
                "model_version": "1.0",
            }

        except Exception as e:
            logging.error(f"Prediction error: {str(e)}")
            raise ValueError(f"Failed to make prediction: {str(e)}")

    def _get_risk_level(self, probability):
        if probability < 0.3:
            return "low"
        elif probability < 0.7:
            return "medium"
        return "high"
