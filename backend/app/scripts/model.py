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
import os

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
        """
        try:
            # Check if model file exists
            if not os.path.exists(settings.MODEL_PATH):
                logger.warning(f"Model file not found at {settings.MODEL_PATH}")
                raise FileNotFoundError(
                    f"Model file not found at {settings.MODEL_PATH}"
                )

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
            return loaded_data  # Return the loaded data for reference

        except FileNotFoundError as e:
            logger.error(f"Model file not found: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Failed to load pre-trained model: {str(e)}")
            raise RuntimeError(f"Model loading failed: {str(e)}")

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

    def train(self, df):
        """
        Train model with MongoDB data
        Args:
            df: DataFrame or list of dicts with training data
        Returns:
            Evaluation metrics
        """
        try:
            # Ensure df is a DataFrame
            if not isinstance(df, pd.DataFrame):
                df = pd.DataFrame(df)

            # If _id column exists (from MongoDB), drop it
            if "_id" in df.columns:
                df = df.drop("_id", axis=1)

            # Convert boolean/string values to numeric if needed
            for col in df.columns:
                if col == "Gender" and df[col].dtype == "object":
                    df[col] = df[col].apply(
                        lambda x: 1 if str(x).lower() == "male" else 0
                    )
                elif df[col].dtype == "bool":
                    df[col] = df[col].astype(int)
                elif col == "dropout_status" and df[col].dtype == "object":
                    df[col] = df[col].apply(
                        lambda x: 1 if str(x).lower() in ["true", "1", "yes"] else 0
                    )

            # Ensure all feature columns exist
            missing_cols = set(self.feature_names) - set(df.columns)
            if missing_cols:
                raise ValueError(f"Missing required columns: {missing_cols}")

            # Log data info for debugging
            logger.info(f"Training DataFrame info: {df.columns.tolist()}")
            logger.info(f"Data types: {df.dtypes.to_dict()}")

            # Prepare data
            X = df[self.feature_names]
            y = df["dropout_status"].astype(int)

            # Create preprocessor if not exists
            if self.preprocessor is None:
                from app.scripts.preprocessing import DropoutPreprocessor

                self.preprocessor = DropoutPreprocessor()
                self.preprocessor.fit(X)

            # Preprocess data
            X_processed = self.preprocessor.transform(X)

            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X_processed, y, test_size=0.2, random_state=42
            )

            # Initialize model if None
            if self.model is None:
                from tensorflow.keras.layers import Dense, Dropout
                from tensorflow.keras.models import Sequential

                self.model = Sequential(
                    [
                        Dense(
                            64, activation="relu", input_shape=(X_processed.shape[1],)
                        ),
                        Dropout(0.2),
                        Dense(32, activation="relu"),
                        Dropout(0.2),
                        Dense(1, activation="sigmoid"),
                    ]
                )

                self.model.compile(
                    optimizer=Adam(learning_rate=0.001),
                    loss="binary_crossentropy",
                    metrics=["accuracy"],
                )

            # Train the model
            history = self.model.fit(
                X_train,
                y_train,
                epochs=10,
                batch_size=32,
                validation_data=(X_test, y_test),
                verbose=1,
            )

            # Evaluate
            metrics = self._evaluate(X_test, y_test)

            # Add training history to metrics
            metrics["history"] = {
                "loss": [float(val) for val in history.history["loss"]],
                "accuracy": [float(val) for val in history.history["accuracy"]],
                "val_loss": [float(val) for val in history.history["val_loss"]],
                "val_accuracy": [float(val) for val in history.history["val_accuracy"]],
            }

            # Save updated model
            self._save()

            return metrics

        except Exception as e:
            logger.error(f"Training failed: {str(e)}")
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
