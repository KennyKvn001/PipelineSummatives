import React, { useState, useEffect } from "react";
import { apiService } from "@/services/api-service";
import { 
  Card, CardContent, CardHeader, CardTitle, CardDescription 
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { 
  Table, TableBody, TableCell, 
  TableHead, TableHeader, TableRow 
} from "@/components/ui/table";
import { toast } from "sonner";
import { Loader2, CheckCircle2, AlertCircle, RotateCw } from "lucide-react";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import { Alert, AlertTitle, AlertDescription } from "@/components/ui/alert";

const RetrainingMonitor: React.FC = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [retrainingStatus, setRetrainingStatus] = useState<any>(null);
  const [latestMetrics, setLatestMetrics] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [pollInterval, setPollInterval] = useState<NodeJS.Timeout | null>(null);
  const [progressValue, setProgressValue] = useState(10); // Default animation value
  const [connectionStatus, setConnectionStatus] = useState<boolean | null>(null);

  // Check MongoDB connection status
  useEffect(() => {
    const checkConnection = async () => {
      try {
        const isConnected = await apiService.checkMongoDBHealth();
        setConnectionStatus(isConnected);
      } catch (err) {
        setConnectionStatus(false);
      }
    };
    
    checkConnection();
    // Check connection every 30 seconds
    const interval = setInterval(checkConnection, 30000);
    
    return () => clearInterval(interval);
  }, []);

  // Fetch retraining status
  const fetchRetrainingStatus = async () => {
    try {
      const response = await apiService.getRetrainingStatus();
      setRetrainingStatus(response);
      
      // Update progress animation based on status
      if (response.status === 'in_progress') {
        // For in-progress, gradually increase up to 90%
        setProgressValue(prev => Math.min(prev + 5, 90));
      } else if (response.status === 'completed') {
        setProgressValue(100);
        stopPolling();
        // Also fetch metrics when complete
        fetchTrainingMetrics();
      } else if (response.status === 'failed') {
        setProgressValue(100);
        stopPolling();
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "Failed to fetch retraining status";
      setError(errorMessage);
      console.error("Retraining status error:", errorMessage);
    }
  };

  // Fetch training metrics
  const fetchTrainingMetrics = async () => {
    try {
      const response = await apiService.getTrainingMetrics();
      setLatestMetrics(response);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "Failed to fetch training metrics";
      setError(errorMessage);
      console.error("Training metrics error:", errorMessage);
    }
  };

  // Start polling for status updates
  const startPolling = () => {
    if (!pollInterval) {
      // Poll every 2 seconds initially
      const interval = setInterval(fetchRetrainingStatus, 2000);
      setPollInterval(interval);
    }
  };

  // Stop polling
  const stopPolling = () => {
    if (pollInterval) {
      clearInterval(pollInterval);
      setPollInterval(null);
    }
  };

  // Start retraining
  const startRetraining = async () => {
    setIsLoading(true);
    setError(null);
    setProgressValue(10); // Reset progress
    
    try {
      // Check MongoDB connection first
      const isConnected = await apiService.checkMongoDBHealth();
      if (!isConnected) {
        toast.error("Database connection unavailable. Please check your MongoDB connection.");
        setIsLoading(false);
        return;
      }
      
      const response = await apiService.retrainModel();
      toast.success(response.message);
      
      // Start polling for status updates
      await fetchRetrainingStatus();
      startPolling();
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "Failed to start retraining";
      setError(errorMessage);
      toast.error(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  // Load initial data
  useEffect(() => {
    const loadInitialData = async () => {
      await fetchRetrainingStatus();
      await fetchTrainingMetrics();
      
      // If retraining is in progress, start polling
      if (retrainingStatus?.status === 'in_progress') {
        startPolling();
      }
    };
    
    loadInitialData();
    
    // Clean up interval on component unmount
    return () => stopPolling();
  }, []);

  // Format date from ISO string
  const formatDate = (dateString: string) => {
    try {
      return new Date(dateString).toLocaleString();
    } catch (e) {
      return dateString;
    }
  };

  // Calculate training duration
  const calculateDuration = (start: string, end: string) => {
    try {
      const startTime = new Date(start).getTime();
      const endTime = new Date(end).getTime();
      const durationMs = endTime - startTime;
      
      // Format as minutes and seconds
      const minutes = Math.floor(durationMs / 60000);
      const seconds = Math.floor((durationMs % 60000) / 1000);
      
      return `${minutes}m ${seconds}s`;
    } catch (e) {
      return "Unknown";
    }
  };

  // render preprocessing progress
  const renderProgressSteps = () => {
    if (!retrainingStatus || retrainingStatus.status !== 'in_progress') return null;
    
    const currentStep = retrainingStatus.current_step || "uploading";
    
    return (
      <div className="mt-4 mb-4">
        <h3 className="text-sm font-medium mb-2">Progress:</h3>
        <div className="flex items-center space-x-2">
          {/* Step 1: Data Upload */}
          <div className="flex flex-col items-center">
            <div className={`w-8 h-8 rounded-full flex items-center justify-center 
              ${currentStep === "uploading" ? "bg-amber-500 text-white animate-pulse" : "bg-green-500 text-white"}`}>
              1
            </div>
            <span className="text-xs mt-1">Upload</span>
          </div>
          
          {/* Connector */}
          <div className="w-8 h-1 bg-gray-300"></div>
          
          {/* Step 2: Preprocessing */}
          <div className="flex flex-col items-center">
            <div className={`w-8 h-8 rounded-full flex items-center justify-center
              ${currentStep === "preprocessing" ? "bg-amber-500 text-white animate-pulse" : 
              (retrainingStatus.preprocessing_completed ? "bg-green-500 text-white" : "bg-gray-300 text-gray-600")}`}>
              2
            </div>
            <span className="text-xs mt-1">Preprocess</span>
          </div>
          
          {/* Connector */}
          <div className="w-8 h-1 bg-gray-300"></div>
          
          {/* Step 3: Training */}
          <div className="flex flex-col items-center">
            <div className={`w-8 h-8 rounded-full flex items-center justify-center
              ${currentStep === "training" ? "bg-amber-500 text-white animate-pulse" : "bg-gray-300 text-gray-600"}`}>
              3
            </div>
            <span className="text-xs mt-1">Train</span>
          </div>
        </div>
        
        {/* Current operation message */}
        <div className="mt-2 text-sm text-gray-600">
          {retrainingStatus.message || "Processing..."}
        </div>
      </div>
    );
  };

  // Render status indicator
  const renderStatusIndicator = () => {
    if (!retrainingStatus) {
      return (
        <div className="p-4 text-center text-muted-foreground">
          <Loader2 className="h-8 w-8 mx-auto mb-2 text-muted animate-spin" />
          <p>Loading retraining status...</p>
        </div>
      );
    }

    let statusElement;
    switch (retrainingStatus.status) {
      case 'in_progress':
        statusElement = (
          <div className="flex items-center p-4 bg-amber-50 border border-amber-200 rounded-md">
            <Loader2 className="h-5 w-5 mr-2 text-amber-500 animate-spin" />
            <div className="flex-1">
              <p className="font-medium text-amber-800">Retraining in progress</p>
              <p className="text-sm text-amber-700">
                Started: {retrainingStatus.started_at ? formatDate(retrainingStatus.started_at) : 'N/A'}
              </p>
              {retrainingStatus.data_points && (
                <p className="text-sm text-amber-700">
                  Training on {retrainingStatus.data_points} data points
                </p>
              )}
              <div className="mt-2">
                <Progress value={progressValue} className="h-2" />
              </div>
            </div>
          </div>
        );
        break;
      case 'completed':
        statusElement = (
          <div className="flex items-center p-4 bg-green-50 border border-green-200 rounded-md">
            <CheckCircle2 className="h-5 w-5 mr-2 text-green-500" />
            <div className="flex-1">
              <p className="font-medium text-green-800">Retraining completed</p>
              {retrainingStatus.started_at && retrainingStatus.completed_at && (
                <p className="text-sm text-green-700">
                  Duration: {calculateDuration(retrainingStatus.started_at, retrainingStatus.completed_at)}
                </p>
              )}
              <p className="text-sm text-green-700">
                Completed: {retrainingStatus.completed_at ? formatDate(retrainingStatus.completed_at) : 'N/A'}
              </p>
              {retrainingStatus.processed_records && (
                <p className="text-sm text-green-700">
                  Processed {retrainingStatus.processed_records} records
                </p>
              )}
            </div>
          </div>
        );
        break;
      case 'failed':
        statusElement = (
          <div className="flex items-center p-4 bg-red-50 border border-red-200 rounded-md">
            <AlertCircle className="h-5 w-5 mr-2 text-red-500" />
            <div className="flex-1">
              <p className="font-medium text-red-800">Retraining failed</p>
              {retrainingStatus.failed_at && (
                <p className="text-sm text-red-700">
                  Failed at: {formatDate(retrainingStatus.failed_at)}
                </p>
              )}
              {retrainingStatus.error && (
                <p className="text-sm text-red-700 mt-1 break-words">
                  Error: {retrainingStatus.error}
                </p>
              )}
            </div>
          </div>
        );
        break;
      default:
        statusElement = (
          <div className="p-4 text-center border rounded-md">
            <p>Status: {retrainingStatus.status || 'unknown'}</p>
            {retrainingStatus.message && (
              <p className="text-sm text-muted-foreground mt-1">{retrainingStatus.message}</p>
            )}
          </div>
        );
    }

    return statusElement;
  };

  // Render metrics table
  const renderMetricsTable = () => {
    if (!latestMetrics || (!latestMetrics.metrics && !latestMetrics?.message?.includes("No"))) {
      return (
        <div className="p-4 text-center text-muted-foreground">
          <Loader2 className="h-8 w-8 mx-auto mb-2 text-muted animate-spin" />
          <p>Loading metrics data...</p>
        </div>
      );
    }
    
    if (latestMetrics.message && latestMetrics.message.includes("No")) {
      return (
        <div className="p-4 text-center text-muted-foreground">
          No metrics available yet. Train the model to generate metrics.
        </div>
      );
    }
    
    const metrics = latestMetrics.metrics;
    
    return (
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Metric</TableHead>
            <TableHead>Value</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          <TableRow>
            <TableCell>Accuracy</TableCell>
            <TableCell>{(metrics.accuracy * 100).toFixed(2)}%</TableCell>
          </TableRow>
          <TableRow>
            <TableCell>Precision</TableCell>
            <TableCell>{(metrics.precision * 100).toFixed(2)}%</TableCell>
          </TableRow>
          <TableRow>
            <TableCell>Recall</TableCell>
            <TableCell>{(metrics.recall * 100).toFixed(2)}%</TableCell>
          </TableRow>
          <TableRow>
            <TableCell>F1 Score</TableCell>
            <TableCell>{(metrics.f1 * 100).toFixed(2)}%</TableCell>
          </TableRow>
          <TableRow>
            <TableCell>ROC AUC</TableCell>
            <TableCell>{(metrics.roc_auc * 100).toFixed(2)}%</TableCell>
          </TableRow>
          <TableRow>
            <TableCell>Data Points</TableCell>
            <TableCell>{metrics.data_points || "Unknown"}</TableCell>
          </TableRow>
          <TableRow>
            <TableCell>Training Date</TableCell>
            <TableCell>{formatDate(latestMetrics.timestamp)}</TableCell>
          </TableRow>
        </TableBody>
      </Table>
    );
  };

  return (
    <div className="grid gap-6">
      {connectionStatus === false && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertTitle>Database Connection Error</AlertTitle>
          <AlertDescription>
            The MongoDB database is currently unavailable. Please check your database connection before attempting to retrain the model.
          </AlertDescription>
        </Alert>
      )}
      
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>Model Retraining</CardTitle>
              <CardDescription>
                Retrain the model with newly uploaded data
              </CardDescription>
            </div>
            <Badge variant={connectionStatus ? "default" : "destructive"}>
              {connectionStatus ? "Connected" : "Disconnected"}
            </Badge>
          </div>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div>
              <Button
                onClick={startRetraining}
                disabled={isLoading || retrainingStatus?.status === 'in_progress' || !connectionStatus}
                className="mb-4"
              >
                {isLoading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Initiating Retraining...
                  </>
                ) : (
                  <>
                    <RotateCw className="mr-2 h-4 w-4" />
                    Start Retraining
                  </>
                )}
              </Button>
              {renderProgressSteps()} 
              {renderStatusIndicator()}
            </div>
            
            <Card>
              <CardHeader>
                <CardTitle>Latest Model Metrics</CardTitle>
              </CardHeader>
              <CardContent>
                {renderMetricsTable()}
              </CardContent>
            </Card>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default RetrainingMonitor;