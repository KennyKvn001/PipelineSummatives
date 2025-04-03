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
        """Load the prediction model from disk."""
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

            logger.info("Model loaded successfully")
            return self.model_data
        except Exception as e:
            logger.error(f"Failed to load model: {str(e)}")
            return None

    def predict(self, student_data: StudentInput):
        """Make prediction for a single student.

        Args:
            student_data: Student input data

        Returns:
            dict: Prediction results with probability and risk level

        Raises:
            ValueError: If model is not loaded or prediction fails
        """
        if not self.model_data:
            self.load_model()

        if not self.model_data or not self.model_data.get("model"):
            raise ValueError("Model could not be loaded")

        try:
            # Log input data for debugging
            logger.info(f"Received prediction request with data: {student_data}")

            # Convert input to DataFrame
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

            # Log DataFrame info for debugging
            logger.debug("Input DataFrame data types:")
            logger.debug(input_df.dtypes)

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

            # Ensure probability is between 0 and 1
            proba = max(0.0, min(1.0, proba))

            prediction_result = {
                "dropout_probability": proba,
                "risk_level": self._get_risk_level(proba),
                "model_version": "1.0",
            }

            logger.info(f"Prediction result: {prediction_result}")
            return prediction_result

        except Exception as e:
            logger.error(f"Prediction error: {str(e)}")
            raise ValueError(f"Failed to make prediction: {str(e)}")

    def _get_risk_level(self, probability):
        """Convert probability to risk level.

        Args:
            probability: Dropout probability (0-1)

        Returns:
            str: Risk level ("low", "medium", or "high")
        """
        if probability < 0.4:
            return "low"
        elif probability < 0.7:
            return "medium"
        return "high"
