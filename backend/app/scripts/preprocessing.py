import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.pipeline import Pipeline
import joblib
from app.config import settings


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

    def save(self):
        joblib.dump(self, settings.PREPROCESSOR_PATH)

    @classmethod
    def load(cls):
        return joblib.load(settings.PREPROCESSOR_PATH)
