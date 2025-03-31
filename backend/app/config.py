from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    # MongoDB Configuration
    MONGODB_URI: str = ""
    MONGO_DB: str = "student_dropout"

    # Model Configuration
    MODEL_PATH: str = str(Path(__file__).parent / "models/model.pkl")
    PREPROCESSOR_PATH: str = str(Path(__file__).parent / "models/preprocessor.pkl")

    # Application Settings
    ENVIRONMENT: str = "development"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
