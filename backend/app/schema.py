from pydantic import BaseModel, Field
from enum import Enum
from typing import Optional
from datetime import datetime


class Gender(str, Enum):
    male = "male"
    female = "female"


class StudentInput(BaseModel):
    Curricular_units_2nd_sem_approved: int = Field(..., ge=0)
    Curricular_units_2nd_sem_grade: float = Field(..., ge=0, le=20)
    Age_at_enrollment: int = Field(..., ge=15, le=70)
    Scholarship_holder: bool
    Tuition_fees_up_to_date: bool
    Debtor: bool
    Gender: Gender


class PredictionOutput(BaseModel):
    probability: float = Field(..., ge=0, le=1)
    risk_level: str
    model_version: str


class TrainingData(BaseModel):
    Curricular_units_2nd_sem_approved: int
    Curricular_units_2nd_sem_grade: float
    Age_at_enrollment: int
    Scholarship_holder: bool
    Tuition_fees_up_to_date: bool
    Debtor: bool
    Gender: Gender
    dropout_status: bool
    processed: bool = False
    processed_at: Optional[datetime] = None
