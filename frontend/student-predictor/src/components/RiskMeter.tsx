import React from "react";

interface RiskMeterProps {
  probability: number;
  riskLevel: "low" | "medium" | "high";
}

const RiskMeter: React.FC<RiskMeterProps> = ({ probability, riskLevel }) => {
  // Ensure probability is a valid number between 0 and 1
  const validProbability = Math.max(0, Math.min(1, 
    typeof probability === 'number' && !isNaN(probability) 
      ? probability 
      : 0
  ));
  
  // Convert probability to percentage for display
  const percentage = Math.round(validProbability * 100);
  
  // Calculate rotation angle based on risk level and probability
  const getRotationAngle = () => {
    switch (riskLevel) {
      case "low":
        // Low risk: 0 to 60 degrees (left side)
        return -90 + validProbability * 60;
      case "medium":
        // Medium risk: 60 to 120 degrees (middle)
        return  -30 + (validProbability * 60);
      case "high":
        // High risk: 120 to 180 degrees (right side)
        return 0 + (validProbability * 60);
      default:
        return 0;
    }
  };
  
  // Determine color based on risk level
  const getRiskColor = (riskLevel: "low" | "medium" | "high") => {
    switch (riskLevel) {
      case "low":
        return "#4ade80"; // Green
      case "medium":
        return "#F97316"; // Orange
      case "high":
        return "#ea384c"; // Red
      default:
        return "#4ade80"; // Default to green
    }
  };
  
  const rotationAngle = getRotationAngle();
  const color = getRiskColor(riskLevel);
  
  return (
    <div className="relative w-64 h-36">
      {/* Semicircle meter background */}
      <div className="absolute w-full h-full bg-gray-200 rounded-t-full overflow-hidden">
        <div 
          className="absolute bottom-0 left-0 w-full h-full bg-gradient-to-r from-green-200 via-orange-300 to-red-400 rounded-t-full"
          style={{ opacity: 0.2 }}
        />
      </div>
      
      {/* Needle */}
      <div 
        className="absolute bottom-0 left-1/2 w-1 h-[95%] bg-gray-800 rounded origin-bottom transition-transform duration-500 ease-in-out"
        style={{ 
          transform: `translateX(-50%) rotate(${rotationAngle}deg)`,
          transformOrigin: 'bottom center'
        }}
      />
      
      {/* Center pivot point */}
      <div className="absolute bottom-0 left-1/2 w-6 h-6 bg-gray-800 rounded-full -translate-x-1/2 translate-y-[25%]" />
      
      {/* Percentage indicator */}
      <div 
        className="absolute bottom-1/3 left-1/2 transform -translate-x-1/2 text-center"
      >
        <div 
          className="text-3xl font-bold"
          style={{ color }}
        >
          {percentage}%
        </div>
        <div 
          className="text-sm font-medium uppercase"
          style={{ color }}
        >
          {riskLevel} Risk
        </div>
      </div>
      
      {/* Risk level markers */}
      <div className="absolute bottom-0 w-full flex justify-between px-4 pb-6">
        <span className="text-xs font-medium text-green-600">LOW</span>
        <span className="text-xs font-medium text-orange-500">MEDIUM</span>
        <span className="text-xs font-medium text-red-500">HIGH</span>
      </div>
    </div>
  );
};

export default RiskMeter;