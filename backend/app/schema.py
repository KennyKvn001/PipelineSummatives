from pydantic import BaseModel, Field
from enum import Enum
from typing import Optional, Literal
from datetime import datetime


class Genders(str, Enum):
    male = "male"
    female = "female"


class StudentInput(BaseModel):
    """Input schema matching your dataset columns"""

    Curricular_units_2nd_sem_approved: float = Field(
        ..., description="Standardized approved units"
    )
    Curricular_units_2nd_sem_grade: float = Field(
        ..., description="Standardized grade score"
    )
    Tuition_fees_up_to_date: Literal[0, 1] = Field(..., description="0=No, 1=Yes")
    Scholarship_holder: Literal[0, 1] = Field(..., description="0=No, 1=Yes")
    Age_at_enrollment: float = Field(..., description="Standardized age value")
    Debtor: Literal[0, 1] = Field(..., description="0=No, 1=Yes")
    Gender: Genders = Field(..., description="1=Male, 0=Female")


class PredictionOutput(BaseModel):
    dropout_probability: float = Field(..., ge=0, le=1)
    risk_level: Literal["low", "medium", "high"]
    model_version: str


class TrainingData(BaseModel):
    Curricular_units_2nd_sem_approved: int
    Curricular_units_2nd_sem_grade: float
    Age_at_enrollment: int
    Scholarship_holder: bool
    Tuition_fees_up_to_date: bool
    Debtor: bool
    Gender: Genders
    dropout_status: bool
    processed: bool = False
    processed_at: Optional[datetime] = None
