
import React from "react";
import AdminDashboard from "@/components/AdminDashboard";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

const AdminPage: React.FC = () => {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Admin Dashboard</h1>
      </div>
      
      <div className="grid gap-6">
        <Card className="shadow-sm">
          <CardHeader className="pb-3">
            <CardTitle>Model Management</CardTitle>
            <CardDescription>
              Upload training data and manage model retraining
            </CardDescription>
          </CardHeader>
          <CardContent>
            <AdminDashboard />
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default AdminPage;
