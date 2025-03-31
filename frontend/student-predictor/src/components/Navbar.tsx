
import React from "react";
import { Bell, Settings, User } from "lucide-react";
import { Button } from "@/components/ui/button";

const Navbar: React.FC = () => {
  return (
    <header className="border-b border-gray-200 bg-white py-3 px-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-semibold text-gray-800">Student Dropout Prediction System</h2>
        </div>
        
        <div className="flex items-center gap-4">
          <Button variant="ghost" size="icon" className="text-gray-500">
            <Bell size={18} />
          </Button>
          <Button variant="ghost" size="icon" className="text-gray-500">
            <Settings size={18} />
          </Button>
          <div className="flex items-center gap-2">
            <div className="h-8 w-8 rounded-full bg-primary flex items-center justify-center text-white">
              <User size={16} />
            </div>
            <span className="text-sm font-medium hidden sm:inline-block">Admin</span>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Navbar;
