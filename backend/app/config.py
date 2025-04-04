from pydantic import BaseSettings
from pathlib import Path
from typing import List
import os


class Settings(BaseSettings):
    # MongoDB Configuration
    MONGODB_URI: str = os.environ.get(
        "MONGODB_URI",
        "mongodb://localhost:27017",
    )
    MONGO_DB: str = os.environ.get("MONGO_DB", "student_dropout")
    MONGO_CONNECT_TIMEOUT_MS: int = 5000
    MONGO_MAX_POOL_SIZE: int = 10
    MONGO_USE_TLS: bool = True

    # Data Validation
    TRAINING_DATA_FIELDS: List[str] = [
        "Curricular_units_2nd_sem_approved",
        "Curricular_units_2nd_sem_grade",
        "Tuition_fees_up_to_date",
        "Scholarship_holder",
        "Age_at_enrollment",
        "Debtor",
        "Gender",
    ]

    # Model Configuration
    MODEL_DIR: Path = Path(__file__).parent / "models"
    MODEL_PATH: str = str(MODEL_DIR / "model_4.pkl")
    PREPROCESSOR_PATH: str = str(MODEL_DIR / "preprocessor.pkl")

    # Application Settings
    ENVIRONMENT: str = os.environ.get("ENVIRONMENT", "development")
    LOG_LEVEL: str = os.environ.get("LOG_LEVEL", "INFO")

    # API Settings
    ENABLE_CORS: bool = os.environ.get("ENABLE_CORS", "True").lower() == "true"
    ALLOWED_ORIGINS: List[str] = ["http://localhost:8000"]

    def get_mongo_connection_options(self) -> dict:
        """Return all MongoDB connection options as a dictionary"""
        return {
            "serverSelectionTimeoutMS": self.MONGO_CONNECT_TIMEOUT_MS,
            "maxPoolSize": self.MONGO_MAX_POOL_SIZE,
        }

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Ensure model directory exists
        self.MODEL_DIR.mkdir(exist_ok=True, parents=True)


# Create a singleton instance of settings to be imported elsewhere
settings = Settings()
