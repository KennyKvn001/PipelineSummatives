
import React from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, Legend } from "recharts";
import { sampleData, sampleCorrelations } from "@/types/api-types";
import { ChartContainer } from "@/components/ui/chart";

const DataInsights: React.FC = () => {
  // Distribution data for risk levels
  const distributionData = [
    { name: "Low Risk", value: sampleData.filter(d => d.risk_level === "low").length },
    { name: "Medium Risk", value: sampleData.filter(d => d.risk_level === "medium").length },
    { name: "High Risk", value: sampleData.filter(d => d.risk_level === "high").length },
  ];

  // Colors for the pie chart
  const COLORS = ["#4ade80", "#F97316", "#ea384c"];
  
  return (
    <div className="grid md:grid-cols-2 gap-6">
      <Card className="md:col-span-1">
        <CardHeader>
          <CardTitle>Risk Level Distribution</CardTitle>
          <CardDescription>
            Distribution of students across different risk categories
          </CardDescription>
        </CardHeader>
        <CardContent className="h-80">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={distributionData}
                cx="50%"
                cy="50%"
                labelLine={false}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
                nameKey="name"
                label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
              >
                {distributionData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip formatter={(value: any) => [`${value} Students`, 'Count']} />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>
      
      <Card className="md:col-span-1">
        <CardHeader>
          <CardTitle>Feature Correlations</CardTitle>
          <CardDescription>
            Impact of different features on dropout risk
          </CardDescription>
        </CardHeader>
        <CardContent className="h-80">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart
              data={sampleCorrelations}
              layout="vertical"
              margin={{
                top: 5,
                right: 30,
                left: 20,
                bottom: 5,
              }}
            >
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis
                type="number"
                domain={[-1, 1]}
                tickFormatter={(value) => value.toFixed(1)}
              />
              <YAxis
                type="category"
                dataKey="feature"
                width={150}
                tickFormatter={(value) => {
                  // Make the feature names more readable
                  return value
                    .replace(/_/g, " ")
                    .split(" ")
                    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
                    .join(" ");
                }}
              />
              <Tooltip 
                formatter={(value: any) => [`${value.toFixed(2)}`, 'Correlation']}
              />
              <Bar 
                dataKey="correlation" 
                fill="#F97316"
                name="Correlation"
              />
            </BarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>
      
      <Card className="md:col-span-2">
        <CardHeader>
          <CardTitle>Historical Prediction Trends</CardTitle>
          <CardDescription>
            Recent trend in student dropout risk predictions
          </CardDescription>
        </CardHeader>
        <CardContent className="h-80">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart
              data={sampleData.map(item => ({
                id: item.id,
                student: item.student_id,
                probability: item.probability,
                risk: item.risk_level,
              }))}
              margin={{
                top: 5,
                right: 30,
                left: 20,
                bottom: 30,
              }}
            >
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis 
                dataKey="student" 
                label={{ 
                  value: 'Student ID', 
                  position: 'insideBottom', 
                  offset: -20 
                }}
              />
              <YAxis 
                domain={[0, 1]}
                tickFormatter={(value) => `${(value * 100).toFixed(0)}%`}
                label={{ 
                  value: 'Dropout Probability', 
                  angle: -90, 
                  position: 'insideLeft' 
                }}
              />
              <Tooltip formatter={(value: any) => [`${(Number(value) * 100).toFixed(1)}%`, 'Probability']} />
              <Bar 
                dataKey="probability" 
                name="Dropout Probability" 
                fill="#F97316"
              />
            </BarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>
    </div>
  );
};

export default DataInsights;
