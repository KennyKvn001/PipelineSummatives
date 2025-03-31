from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import pandas as pd
import joblib
from app.config import settings
from .preprocessing import DropoutPreprocessor


class DropoutModel:
    def __init__(self):
        self.model = RandomForestClassifier(
            n_estimators=100, max_depth=5, class_weight="balanced", random_state=42
        )
        self.preprocessor = DropoutPreprocessor()

    def train(self, data_path: str):
        """Train model from CSV data"""
        df = pd.read_csv(data_path)
        X = df.drop("dropout_status", axis=1)
        y = df["dropout_status"]

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        self.preprocessor.fit(X_train)
        X_train_processed = self.preprocessor.transform(X_train)

        self.model.fit(X_train_processed, y_train)
        self.save()

        return self.evaluate(X_test, y_test)

    def evaluate(self, X_test, y_test):
        from sklearn.metrics import (
            accuracy_score,
            precision_score,
            recall_score,
            f1_score,
            roc_auc_score,
            confusion_matrix,
        )

        X_test_processed = self.preprocessor.transform(X_test)
        y_pred = self.model.predict(X_test_processed)

        return {
            "accuracy": accuracy_score(y_test, y_pred),
            "precision": precision_score(y_test, y_pred),
            "recall": recall_score(y_test, y_pred),
            "f1": f1_score(y_test, y_pred),
            "roc_auc": roc_auc_score(y_test, y_pred),
            "confusion_matrix": confusion_matrix(y_test, y_pred).tolist(),
        }

    def save(self):
        """Save both model and preprocessor"""
        joblib.dump(
            {"model": self.model, "preprocessor": self.preprocessor},
            settings.MODEL_PATH,
        )

    @classmethod
    def load(cls):
        """Load trained model"""
        return joblib.load(settings.MODEL_PATH)
