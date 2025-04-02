from pydantic import BaseModel, Field, validator
from enum import Enum
from typing import Optional, Literal, Union
from datetime import datetime


class Genders(str, Enum):
    male = "male"
    female = "female"


class StudentInput(BaseModel):
    """Input schema matching your dataset columns - for internal model use with standardized values"""

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
    Gender: Union[Genders, int] = Field(
        ..., description="male/female or 1=Male, 0=Female"
    )

    # Convert Gender enum to numeric if needed
    @validator("Gender")
    def validate_gender(cls, v):
        if isinstance(v, Genders):
            return 1 if v == Genders.male else 0
        return v


class UserFriendlyInput(BaseModel):
    """User-friendly input schema with natural value ranges"""

    Curricular_units_2nd_sem_approved: int = Field(
        ..., ge=0, le=20, description="Number of approved units (0-20)"
    )
    Curricular_units_2nd_sem_grade: float = Field(
        ..., ge=0, le=20, description="Grade score (0-20)"
    )
    Tuition_fees_up_to_date: bool = Field(
        ..., description="Are tuition fees up to date?"
    )
    Scholarship_holder: bool = Field(
        ..., description="Does the student have a scholarship?"
    )
    Age_at_enrollment: int = Field(
        ..., ge=17, le=70, description="Student's age at enrollment"
    )
    Debtor: bool = Field(..., description="Is the student a debtor?")
    Gender: Genders = Field(..., description="Student's gender (male/female)")


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
