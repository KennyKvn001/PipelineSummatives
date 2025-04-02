import numpy as np
from app.schema import UserFriendlyInput, StudentInput

# Define the standardization parameters
# Note: Replace these with the actual values from your model training
STANDARDIZATION_PARAMS = {
    "Curricular_units_2nd_sem_approved": {"mean": 10.5, "std": 4.6},  # Example values
    "Curricular_units_2nd_sem_grade": {"mean": 12.3, "std": 3.8},  # Example values
    "Age_at_enrollment": {"mean": 23.5, "std": 6.2},  # Example values
}


def transform_user_input(user_input: UserFriendlyInput) -> StudentInput:
    """Transform user-friendly values to standardized model input"""

    # Standardize numeric values
    standardized_approved = (
        user_input.Curricular_units_2nd_sem_approved
        - STANDARDIZATION_PARAMS["Curricular_units_2nd_sem_approved"]["mean"]
    ) / STANDARDIZATION_PARAMS["Curricular_units_2nd_sem_approved"]["std"]

    standardized_grade = (
        user_input.Curricular_units_2nd_sem_grade
        - STANDARDIZATION_PARAMS["Curricular_units_2nd_sem_grade"]["mean"]
    ) / STANDARDIZATION_PARAMS["Curricular_units_2nd_sem_grade"]["std"]

    standardized_age = (
        user_input.Age_at_enrollment
        - STANDARDIZATION_PARAMS["Age_at_enrollment"]["mean"]
    ) / STANDARDIZATION_PARAMS["Age_at_enrollment"]["std"]

    # Convert boolean to int
    tuition_up_to_date = 1 if user_input.Tuition_fees_up_to_date else 0
    scholarship = 1 if user_input.Scholarship_holder else 0
    debtor = 1 if user_input.Debtor else 0
    gender = 1 if user_input.Gender.lower() == "male" else 0

    # Create model input
    return StudentInput(
        Curricular_units_2nd_sem_approved=standardized_approved,
        Curricular_units_2nd_sem_grade=standardized_grade,
        Tuition_fees_up_to_date=tuition_up_to_date,
        Scholarship_holder=scholarship,
        Age_at_enrollment=standardized_age,
        Debtor=debtor,
        Gender=gender,
    )


# Function to reverse the transformation (for displaying model results in user terms)
def reverse_transform(standardized_value, feature_name):
    """Convert standardized value back to original scale"""
    if feature_name in STANDARDIZATION_PARAMS:
        params = STANDARDIZATION_PARAMS[feature_name]
        return (standardized_value * params["std"]) + params["mean"]
    return standardized_value
