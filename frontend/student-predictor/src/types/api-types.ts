
// Input interface that must match backend schema exactly
export interface PredictionInput {
  Curricular_units_2nd_sem_approved: number;
  Curricular_units_2nd_sem_grade: number;
  Tuition_fees_up_to_date: 0 | 1;
  Scholarship_holder: 0 | 1;
  Age_at_enrollment: number;
  Debtor: 0 | 1;
  Gender: 0 | 1;
}

export interface UserFriendlyPredictionInput {
  Curricular_units_2nd_sem_approved: number;
  Curricular_units_2nd_sem_grade: number;
  Tuition_fees_up_to_date: boolean;
  Scholarship_holder: boolean;
  Age_at_enrollment: number;
  Debtor: boolean;
  Gender: string;
}

// Response interface from prediction endpoint
export interface PredictionResponse {
  probability: number;
  risk_level: "low" | "medium" | "high";
}

// API error response
export interface ApiError {
  detail: string;
}

// Training history entry
export interface TrainingHistoryEntry {
  id: string;
  timestamp: string;
  accuracy: number;
  data_size: number;
}

// Sample data for testing
export const sampleData = [
  { 
    id: "1",
    probability: 0.2,
    risk_level: "low",
    timestamp: "2023-01-15T10:30:00Z",
    student_id: "S12345"
  },
  { 
    id: "2",
    probability: 0.5,
    risk_level: "medium",
    timestamp: "2023-01-18T14:45:00Z",
    student_id: "S12346"
  },
  { 
    id: "3",
    probability: 0.85,
    risk_level: "high",
    timestamp: "2023-01-20T09:15:00Z", 
    student_id: "S12347"
  },
  { 
    id: "4",
    probability: 0.35,
    risk_level: "low",
    timestamp: "2023-01-22T16:20:00Z", 
    student_id: "S12348"
  },
  { 
    id: "5",
    probability: 0.75,
    risk_level: "high",
    timestamp: "2023-01-25T11:10:00Z", 
    student_id: "S12349"
  }
];

// Sample training history for testing
export const sampleTrainingHistory: TrainingHistoryEntry[] = [
  {
    id: "1",
    timestamp: "2023-01-10T09:30:00Z",
    accuracy: 0.87,
    data_size: 5000
  },
  {
    id: "2",
    timestamp: "2023-02-15T14:45:00Z",
    accuracy: 0.89,
    data_size: 5500
  },
  {
    id: "3",
    timestamp: "2023-03-20T11:15:00Z",
    accuracy: 0.91,
    data_size: 6200
  },
  {
    id: "4",
    timestamp: "2023-04-25T10:00:00Z",
    accuracy: 0.90,
    data_size: 6800
  }
];

// Feature correlations sample data
export const sampleCorrelations = [
  { feature: "Curricular_units_2nd_sem_approved", correlation: 0.75 },
  { feature: "Curricular_units_2nd_sem_grade", correlation: 0.68 },
  { feature: "Tuition_fees_up_to_date", correlation: -0.52 },
  { feature: "Scholarship_holder", correlation: -0.45 },
  { feature: "Age_at_enrollment", correlation: 0.38 },
  { feature: "Debtor", correlation: 0.62 },
  { feature: "Gender", correlation: 0.15 }
];
