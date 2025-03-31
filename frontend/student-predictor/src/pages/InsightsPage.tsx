
import React from "react";
import DataInsights from "@/components/DataInsights";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

const InsightsPage: React.FC = () => {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Data Insights</h1>
      </div>
      
      <Card className="shadow-sm">
        <CardHeader className="pb-3">
          <CardTitle>Analytics Overview</CardTitle>
          <CardDescription>
            Visualizations of student dropout risk data and trends
          </CardDescription>
        </CardHeader>
        <CardContent>
          <DataInsights />
        </CardContent>
      </Card>
    </div>
  );
};

export default InsightsPage;
