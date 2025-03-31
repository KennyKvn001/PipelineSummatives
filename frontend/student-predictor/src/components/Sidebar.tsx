
import React, { useState } from "react";
import { NavLink } from "react-router-dom";
import { BarChart3, FileInput, Home, ChevronLeft, ChevronRight } from "lucide-react";
import { cn } from "@/lib/utils";

export const Sidebar = () => {
  const [collapsed, setCollapsed] = useState(false);

  const navItems = [
    { path: "/", label: "Prediction", icon: Home },
    { path: "/admin", label: "Admin", icon: FileInput },
    { path: "/insights", label: "Insights", icon: BarChart3 },
  ];

  return (
    <div className={cn(
      "bg-white border-r border-gray-200 transition-all duration-300 flex flex-col",
      collapsed ? "w-[70px]" : "w-[250px]"
    )}>
      <div className="p-4 flex items-center justify-between border-b border-gray-200">
        {!collapsed && (
          <h1 className="font-bold text-lg">StudentPredictor</h1>
        )}
        <button
          onClick={() => setCollapsed(!collapsed)}
          className="p-1.5 rounded-md hover:bg-gray-100"
        >
          {collapsed ? <ChevronRight size={18} /> : <ChevronLeft size={18} />}
        </button>
      </div>
      
      <nav className="flex-1 py-6 px-3">
        <div className="space-y-1">
          {navItems.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) => cn(
                "flex items-center gap-3 py-2 px-3 rounded-md text-sm font-medium transition-colors",
                isActive ? 
                  "bg-primary text-primary-foreground" : 
                  "text-gray-600 hover:bg-gray-100 hover:text-gray-900"
              )}
            >
              <item.icon size={18} />
              {!collapsed && <span>{item.label}</span>}
            </NavLink>
          ))}
        </div>
      </nav>
      
      <div className="p-4 border-t border-gray-200">
        {!collapsed && (
          <div className="bg-blue-50 text-blue-700 rounded-md p-3 text-xs">
            <p className="font-medium">Prediction Accuracy</p>
            <p className="text-lg font-bold mt-1">91%</p>
          </div>
        )}
      </div>
    </div>
  );
};
