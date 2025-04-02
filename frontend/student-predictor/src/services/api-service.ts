import axios, { AxiosError } from "axios";
import { PredictionResponse, ApiError, TrainingHistoryEntry, UserFriendlyPredictionInput } from "@/types/api-types";

// Create axios instance with base configuration
const api = axios.create({
  baseURL: "http://localhost:8000", // Default backend URL, can be updated with env vars
  headers: {
    "Content-Type": "application/json",
  },
});

export const apiService = {
  // Prediction endpoint
  async predict(input: UserFriendlyPredictionInput): Promise<UserFriendlyPredictionInput> {
    try {
      // Create properly formatted input ensuring numeric fields are actually numbers
      const formattedInput = {
        ...input,
        Curricular_units_2nd_sem_approved: Number(input.Curricular_units_2nd_sem_approved),
        Curricular_units_2nd_sem_grade: Number(input.Curricular_units_2nd_sem_grade),
        Age_at_enrollment: Number(input.Age_at_enrollment),
        Tuition_fees_up_to_date: Number(input.Tuition_fees_up_to_date),
        Scholarship_holder: Number(input.Scholarship_holder),
        Debtor: Number(input.Debtor)
      };

      const response = await api.post<UserFriendlyPredictionInput>("/predict", formattedInput);
      return response.data;
    } catch (error) {
        const axiosError = error as AxiosError<ApiError>;
        if (axiosError.response?.data) {
            // Extract and format the error message properly
            let errorMessage = "An error occurred with the prediction";
            
            if (typeof axiosError.response.data === 'object' && axiosError.response.data.detail) {
                errorMessage = axiosError.response.data.detail;
            } else if (typeof axiosError.response.data === 'string') {
                errorMessage = axiosError.response.data;
            }
            
            throw new Error(`Prediction error: ${errorMessage}`);
        }
        if (axiosError.request) {
            // Request was made but no response received
            throw new Error("Network error: No response received from server");
        }
        throw new Error("Failed to make prediction request");
    }
  },

  // Upload CSV data endpoint
  async uploadCsv(file: File): Promise<{ success: boolean; message: string }> {
    try {
      const formData = new FormData();
      formData.append("file", file);

      const response = await api.post("/upload-data", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });
      return { success: true, message: "Data uploaded successfully" };
    } catch (error) {
      const axiosError = error as AxiosError<ApiError>;
      if (axiosError.response?.data) {
        const errorDetail = typeof axiosError.response.data === 'object' && axiosError.response.data.detail
          ? axiosError.response.data.detail
          : JSON.stringify(axiosError.response.data);
        throw new Error(errorDetail);
      }
      throw new Error("Network error occurred during file upload");
    }
  },

  // Retrain model endpoint
  async retrainModel(): Promise<{ success: boolean; message: string }> {
    try {
      const response = await api.post("/retrain");
      return { 
        success: true, 
        message: response.data?.message || "Model retraining initiated successfully" 
      };
    } catch (error) {
      const axiosError = error as AxiosError<ApiError>;
      if (axiosError.response?.data) {
        const errorDetail = typeof axiosError.response.data === 'object' && axiosError.response.data.detail
          ? axiosError.response.data.detail
          : JSON.stringify(axiosError.response.data);
        throw new Error(errorDetail);
      }
      throw new Error("Network error occurred during model retraining");
    }
  },

  // Get training history (simulated for now)
  async getTrainingHistory(): Promise<TrainingHistoryEntry[]> {
    // In a real implementation, this would make an API call
    // For now, we'll simulate a response
    return new Promise((resolve) => {
      setTimeout(() => {
        const history = [
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
        resolve(history);
      }, 500);
    });
  }
};