
import axios, { AxiosError } from "axios";
import { PredictionInput, PredictionResponse, ApiError, TrainingHistoryEntry } from "@/types/api-types";

// Create axios instance with base configuration
const api = axios.create({
  baseURL: "http://localhost:8000", // Default backend URL, can be updated with env vars
  headers: {
    "Content-Type": "application/json",
  },
});

export const apiService = {
  // Prediction endpoint
  async predict(input: PredictionInput): Promise<PredictionResponse> {
    try {
      const response = await api.post<PredictionResponse>("/predict", input);
      return response.data;
    } catch (error) {
      const axiosError = error as AxiosError<ApiError>;
      if (axiosError.response?.data) {
        throw new Error(axiosError.response.data.detail || "Error making prediction");
      }
      throw new Error("Network error occurred");
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
        throw new Error(axiosError.response.data.detail || "Error uploading data");
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
        throw new Error(axiosError.response.data.detail || "Error retraining model");
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
