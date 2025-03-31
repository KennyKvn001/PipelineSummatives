
import React from "react";
import PredictionForm from "@/components/PredictionForm";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

const PredictionPage: React.FC = () => {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Student Dropout Prediction</h1>
      </div>
      
      <div className="grid gap-6">
        <Card className="shadow-sm">
          <CardHeader className="pb-3">
            <CardTitle>Prediction Form</CardTitle>
            <CardDescription>
              Enter student details to predict dropout risk
            </CardDescription>
          </CardHeader>
          <CardContent>
            <PredictionForm />
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default PredictionPage;
