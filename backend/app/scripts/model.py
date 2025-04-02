import joblib
import pandas as pd
import numpy as np
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.optimizers import Adam
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
)
from typing import Dict, Any
import logging
from app.config import settings

logger = logging.getLogger(__name__)


class DropoutModel:
    def __init__(self):
        """Initialize with placeholder model and preprocessor"""
        self.model = None
        self.preprocessor = None
        self.feature_names = [
            "Curricular_units_2nd_sem_approved",
            "Curricular_units_2nd_sem_grade",
            "Tuition_fees_up_to_date",
            "Scholarship_holder",
            "Age_at_enrollment",
            "Debtor",
            "Gender",
        ]

    def load_pretrained(self) -> None:
        """
        Load pre-trained model from .pkl file
        Expected .pkl format: {
            'model': Keras Sequential model,
            'preprocessor': sklearn preprocessor,
            'metadata': dict (optional)
        }
        """
        try:
            loaded_data = joblib.load(settings.MODEL_PATH)

            # Check if it's already a Sequential model (not a dict)
            if isinstance(loaded_data, Sequential):
                self.model = loaded_data
                self.preprocessor = None
                logger.info("Loaded Sequential model successfully")
            else:
                # It's a dictionary with both model and preprocessor
                if not all(k in loaded_data for k in ["model", "preprocessor"]):
                    raise ValueError(
                        "Invalid .pkl structure. Expected keys: 'model', 'preprocessor'"
                    )

                self.model = loaded_data["model"]
                self.preprocessor = loaded_data["preprocessor"]

            logger.info("Pre-trained model loaded successfully")

        except Exception as e:
            logger.error(f"Failed to load pre-trained model: {str(e)}")
            raise RuntimeError("Model loading failed. Check logs for details.")

    def predict(self, input_data: pd.DataFrame) -> Dict[str, Any]:
        """
        Make prediction using loaded model
        Args:
            input_data: DataFrame with exact feature_names columns
        Returns:
            {'probability': float, 'risk_level': str}
        """
        try:
            # Check if model is loaded
            if self.model is None:
                raise ValueError("Model is not loaded. Call load_pretrained() first.")

            # Validate input
            if not set(self.feature_names).issubset(input_data.columns):
                missing = set(self.feature_names) - set(input_data.columns)
                raise ValueError(f"Missing features: {missing}")

            # Get features in the correct order
            X = input_data[self.feature_names].values

            # Apply preprocessing only if preprocessor exists
            if self.preprocessor is not None:
                X_processed = self.preprocessor.transform(X)
            else:
                # Assume data is already in the correct format for the model
                X_processed = X

            # Debug print
            logger.info(f"Input shape: {X_processed.shape}")

            # Predict with error checking
            predictions = self.model.predict(X_processed)

            # Debug print
            logger.info(f"Prediction result type: {type(predictions)}")
            logger.info(
                f"Prediction result shape: {predictions.shape if hasattr(predictions, 'shape') else 'no shape'}"
            )
            logger.info(f"Prediction result: {predictions}")

            # Safely extract probability value
            if predictions is None:
                raise ValueError("Model prediction returned None")

            # Handle different prediction formats
            if hasattr(predictions, "shape") and len(predictions.shape) > 1:
                proba = float(predictions[0][0])
            else:
                proba = float(predictions[0])

            return {
                "probability": proba,
                "risk_level": (
                    "high" if proba > 0.7 else "medium" if proba > 0.4 else "low"
                ),
            }

        except Exception as e:
            logger.error(f"Prediction failed: {str(e)}")
            # Re-raise with more context
            raise ValueError(f"Prediction failed: {str(e)}")

    def retrain(self, new_data_path: str, epochs: int = 10) -> Dict[str, Any]:
        """
        Retrain model with new data while preserving pretrained weights
        Args:
            new_data_path: Path to CSV with new training data
            epochs: Number of training epochs
        Returns:
            Evaluation metrics on test set
        """
        try:
            # Load new data
            new_data = pd.read_csv(new_data_path)

            # Validate
            required_cols = set(self.feature_names + ["dropout_status"])
            if not required_cols.issubset(new_data.columns):
                missing = required_cols - set(new_data.columns)
                raise ValueError(f"New data missing columns: {missing}")

            # Prepare data
            X_new = new_data[self.feature_names].values
            y_new = new_data["dropout_status"].values
            X_new_processed = self.preprocessor.transform(X_new)

            # Transfer learning
            self.model.fit(
                X_new_processed,
                y_new,
                epochs=epochs,
                batch_size=32,
                validation_split=0.2,
                verbose=1,
            )

            # Evaluate
            X_test, y_test = train_test_split(
                (X_new_processed, y_new), test_size=0.3, random_state=42
            )

            metrics = self._evaluate(X_test, y_test)

            # Save updated model
            self._save()

            return metrics

        except Exception as e:
            logger.error(f"Retraining failed: {str(e)}")
            raise

    def _evaluate(self, X_test: np.ndarray, y_test: np.ndarray) -> Dict[str, Any]:
        """Internal evaluation method"""
        y_pred = (self.model.predict(X_test) > 0.5).astype(int)
        y_proba = self.model.predict(X_test)

        return {
            "accuracy": accuracy_score(y_test, y_pred),
            "precision": precision_score(y_test, y_pred),
            "recall": recall_score(y_test, y_pred),
            "f1": f1_score(y_test, y_pred),
            "roc_auc": roc_auc_score(y_test, y_proba),
            "confusion_matrix": confusion_matrix(y_test, y_pred).tolist(),
        }

    def _save(self) -> None:
        """Save current model state"""
        try:
            joblib.dump(
                {
                    "model": self.model,
                    "preprocessor": self.preprocessor,
                    "feature_names": self.feature_names,
                    "metadata": {"retrained_at": pd.Timestamp.now().isoformat()},
                },
                settings.MODEL_PATH,
            )
            logger.info(f"Model saved to {settings.MODEL_PATH}")
        except Exception as e:
            logger.error(f"Failed to save model: {str(e)}")
            raise


# Singleton instance to be imported elsewhere
dropout_model = DropoutModel()
