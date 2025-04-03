import React, { useState, useEffect } from "react";
import { apiService } from "@/services/api-service";
import { TrainingHistoryEntry } from "@/types/api-types";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { toast } from "sonner";
import { FileInput, RefreshCw } from "lucide-react";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { format } from "date-fns";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import RetrainingMonitor from "./RetrainingMonitor";

const AdminDashboard: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [trainingHistory, setTrainingHistory] = useState<TrainingHistoryEntry[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Load training history
    const loadTrainingHistory = async () => {
      try {
        const history = await apiService.getTrainingHistory();
        setTrainingHistory(history);
      } catch (error) {
        toast.error("Failed to load training history");
      } finally {
        setIsLoading(false);
      }
    };

    loadTrainingHistory();
  }, []);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selectedFile = e.target.files[0];
      
      // Ensure it's a CSV file
      if (!selectedFile.name.endsWith('.csv')) {
        toast.error("Please select a CSV file");
        return;
      }
      
      setFile(selectedFile);
    }
  };

  const handleUpload = async () => {
    if (!file) {
      toast.error("Please select a file first");
      return;
    }

    setIsUploading(true);
    try {
      await apiService.uploadCsv(file);
      toast.success("Data uploaded successfully");
      setFile(null);
      // Reset the file input
      const fileInput = document.getElementById("csvFile") as HTMLInputElement;
      if (fileInput) fileInput.value = "";
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "Failed to upload file");
    } finally {
      setIsUploading(false);
    }
  };

  // Format date from ISO string
  const formatDate = (dateString: string) => {
    try {
      return format(new Date(dateString), 'MMM d, yyyy - h:mm a');
    } catch (e) {
      return dateString;
    }
  };

  return (
    <div className="grid gap-6">
      <Tabs defaultValue="upload">
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="upload">Upload Training Data</TabsTrigger>
          <TabsTrigger value="retrain">Model Training</TabsTrigger>
        </TabsList>
        
        <TabsContent value="upload" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Upload Training Data</CardTitle>
              <CardDescription>
                Upload CSV files with student data to improve the model's predictions.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex flex-col gap-4">
                <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
                  <FileInput className="mx-auto h-12 w-12 text-gray-400 mb-2" />
                  <p className="text-sm text-gray-600">
                    Drag and drop a CSV file here, or click to select
                  </p>
                  <p className="text-xs text-gray-400 mt-1">
                    Must include same fields as prediction form plus dropout_status column (0/1)
                  </p>
                  <input
                    id="csvFile"
                    type="file"
                    accept=".csv"
                    onChange={handleFileChange}
                    className="mt-4 w-full max-w-xs mx-auto text-sm"
                  />
                </div>
                
                {file && (
                  <div className="flex items-center justify-between p-3 bg-muted rounded-md">
                    <span className="text-sm font-medium">{file.name}</span>
                    <Button
                      onClick={handleUpload}
                      disabled={isUploading}
                      className="ml-3"
                    >
                      {isUploading ? "Uploading..." : "Upload"}
                    </Button>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>

          {/* <Card>
            <CardHeader>
              <CardTitle>Training History</CardTitle>
              <CardDescription>
                History of previous model training sessions
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="rounded-md overflow-hidden">
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Date</TableHead>
                        <TableHead>Dataset Size</TableHead>
                        <TableHead>Accuracy</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {isLoading ? (
                        <TableRow>
                          <TableCell colSpan={3} className="text-center py-8">Loading...</TableCell>
                        </TableRow>
                      ) : trainingHistory.length === 0 ? (
                        <TableRow>
                          <TableCell colSpan={3} className="text-center py-8">No training history available</TableCell>
                        </TableRow>
                      ) : (
                        trainingHistory.map((entry) => (
                          <TableRow key={entry.id}>
                            <TableCell>{formatDate(entry.timestamp)}</TableCell>
                            <TableCell>{entry.data_size.toLocaleString()}</TableCell>
                            <TableCell>{(entry.accuracy * 100).toFixed(1)}%</TableCell>
                          </TableRow>
                        ))
                      )}
                    </TableBody>
                  </Table>
                </div>
              </div>
            </CardContent>
          </Card> */}
        </TabsContent>
        
        <TabsContent value="retrain">
          <RetrainingMonitor />
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default AdminDashboard;