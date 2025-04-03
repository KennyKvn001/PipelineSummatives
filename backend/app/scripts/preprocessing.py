import pandas as pd
import numpy as np
import logging
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.pipeline import Pipeline
import joblib
from app.config import settings


logger = logging.getLogger(__name__)


class DropoutPreprocessor:
    def __init__(self):
        self.numeric_features = [
            "Curricular_units_2nd_sem_approved",
            "Curricular_units_2nd_sem_grade",
            "Age_at_enrollment",
        ]
        self.categorical_features = [
            "Scholarship_holder",
            "Tuition_fees_up_to_date",
            "Debtor",
            "Gender",
        ]
        self.preprocessor = self._build_preprocessor()

    def _build_preprocessor(self):
        numeric_transformer = Pipeline(steps=[("scaler", StandardScaler())])

        categorical_transformer = Pipeline(
            steps=[("onehot", OneHotEncoder(handle_unknown="ignore"))]
        )

        return ColumnTransformer(
            transformers=[
                ("num", numeric_transformer, self.numeric_features),
                ("cat", categorical_transformer, self.categorical_features),
            ]
        )

    def fit(self, X, y=None):
        self.preprocessor.fit(X)
        return self

    def transform(self, X):
        return self.preprocessor.transform(X)

    def preprocess_for_retraining(self, df):
        """
        Prepares uploaded data for retraining by cleaning, converting data types,
        and applying appropriate transformations.

        Args:
            df: DataFrame with the uploaded data

        Returns:
            Processed DataFrame ready for model training
        """
        try:
            # Create a copy to avoid modifying the original
            processed_df = df.copy()

            # Remove MongoDB ID if present
            if "_id" in processed_df.columns:
                processed_df = processed_df.drop("_id", axis=1)

            # Log preprocessing start
            logger.info(f"Preprocessing DataFrame with shape: {processed_df.shape}")
            logger.info(f"Columns: {processed_df.columns.tolist()}")

            # Format data types - convert categorical variables to proper format
            for col in self.categorical_features:
                if col in processed_df.columns:
                    if col == "Gender" and processed_df[col].dtype == "object":
                        processed_df[col] = processed_df[col].apply(
                            lambda x: 1 if str(x).lower() == "male" else 0
                        )
                    elif (
                        processed_df[col].dtype == "object"
                        or processed_df[col].dtype == "bool"
                    ):
                        processed_df[col] = processed_df[col].apply(
                            lambda x: (
                                1 if str(x).lower() in ["true", "1", "yes", "t"] else 0
                            )
                        )

            # Convert target column if present
            if "dropout_status" in processed_df.columns:
                if (
                    processed_df["dropout_status"].dtype == "object"
                    or processed_df["dropout_status"].dtype == "bool"
                ):
                    processed_df["dropout_status"] = processed_df[
                        "dropout_status"
                    ].apply(
                        lambda x: (
                            1 if str(x).lower() in ["true", "1", "yes", "t"] else 0
                        )
                    )

            # Ensure numeric columns are indeed numeric
            for col in self.numeric_features:
                if col in processed_df.columns:
                    processed_df[col] = pd.to_numeric(
                        processed_df[col], errors="coerce"
                    )

            # Handle missing values if any
            for col in self.numeric_features:
                if col in processed_df.columns and processed_df[col].isnull().any():
                    # Fill missing values with mean
                    mean_value = processed_df[col].mean()
                    processed_df[col] = processed_df[col].fillna(mean_value)
                    logger.info(
                        f"Filled missing values in {col} with mean: {mean_value}"
                    )

            # Log preprocessing completion
            logger.info(f"Preprocessing completed. Final shape: {processed_df.shape}")

            return processed_df

        except Exception as e:
            logger.error(f"Error during preprocessing for retraining: {str(e)}")
            raise

    def save(self):
        joblib.dump(self, settings.PREPROCESSOR_PATH)

    @classmethod
    def load(cls):
        return joblib.load(settings.PREPROCESSOR_PATH)
