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
import { Loader2, CheckCircle2, AlertCircle } from "lucide-react";
import { Progress } from "@/components/ui/progress";

const RetrainingMonitor: React.FC = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [retrainingStatus, setRetrainingStatus] = useState<any>(null);
  const [latestMetrics, setLatestMetrics] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [pollInterval, setPollInterval] = useState<NodeJS.Timeout | null>(null);

  // Fetch retraining status
  const fetchRetrainingStatus = async () => {
    try {
      const response = await apiService.getRetrainingStatus();
      setRetrainingStatus(response);
      
      // If retraining is complete, fetch metrics and stop polling
      if (response.status === 'completed') {
        fetchTrainingMetrics();
        stopPolling();
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "Failed to fetch retraining status";
      setError(errorMessage);
      toast.error(errorMessage);
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
      toast.error(errorMessage);
    }
  };

  // Start polling for status updates
  const startPolling = () => {
    if (!pollInterval) {
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
    
    try {
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

  // Render status indicator
  const renderStatusIndicator = () => {
    if (!retrainingStatus) {
      return <div className="p-4 text-center text-muted-foreground">No retraining information available</div>;
    }

    let statusElement;
    switch (retrainingStatus.status) {
      case 'in_progress':
        statusElement = (
          <div className="flex items-center p-4 bg-amber-50 border border-amber-200 rounded-md">
            <Loader2 className="h-5 w-5 mr-2 text-amber-500 animate-spin" />
            <div>
              <p className="font-medium text-amber-800">Retraining in progress</p>
              <p className="text-sm text-amber-700">
                Started: {retrainingStatus.started_at ? formatDate(retrainingStatus.started_at) : 'N/A'}
              </p>
              <div className="mt-2">
                <Progress value={30} className="h-2" />
              </div>
            </div>
          </div>
        );
        break;
      case 'completed':
        statusElement = (
          <div className="flex items-center p-4 bg-green-50 border border-green-200 rounded-md">
            <CheckCircle2 className="h-5 w-5 mr-2 text-green-500" />
            <div>
              <p className="font-medium text-green-800">Retraining completed</p>
              <p className="text-sm text-green-700">
                Completed: {retrainingStatus.completed_at ? formatDate(retrainingStatus.completed_at) : 'N/A'}
              </p>
            </div>
          </div>
        );
        break;
      case 'failed':
        statusElement = (
          <div className="flex items-center p-4 bg-red-50 border border-red-200 rounded-md">
            <AlertCircle className="h-5 w-5 mr-2 text-red-500" />
            <div>
              <p className="font-medium text-red-800">Retraining failed</p>
              {retrainingStatus.error && <p className="text-sm text-red-700">Error: {retrainingStatus.error}</p>}
            </div>
          </div>
        );
        break;
      default:
        statusElement = (
          <div className="p-4 text-center border rounded-md">
            <p>Status: {retrainingStatus.status || 'unknown'}</p>
          </div>
        );
    }

    return statusElement;
  };

  // Render metrics table
  const renderMetricsTable = () => {
    if (!latestMetrics || !latestMetrics.metrics) {
      return <div className="p-4 text-center text-muted-foreground">No metrics available yet</div>;
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
            <TableCell>Training Date</TableCell>
            <TableCell>{formatDate(latestMetrics.timestamp)}</TableCell>
          </TableRow>
        </TableBody>
      </Table>
    );
  };

  return (
    <div className="grid gap-6">
      <Card>
        <CardHeader>
          <CardTitle>Model Retraining</CardTitle>
          <CardDescription>
            Retrain the model with newly uploaded data
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div>
              <Button
                onClick={startRetraining}
                disabled={isLoading || retrainingStatus?.status === 'in_progress'}
                className="mb-4"
              >
                {isLoading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Initiating Retraining...
                  </>
                ) : (
                  "Start Retraining"
                )}
              </Button>
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