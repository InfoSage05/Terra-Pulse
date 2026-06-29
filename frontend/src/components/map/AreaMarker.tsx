import React from "react";
import { AdvancedMarker } from "@vis.gl/react-google-maps";
import { AlertTriangle } from "lucide-react";

interface AreaMarkerProps {
  lat: number;
  lng: number;
  needsReview: boolean;
  onClick: () => void;
}

export function AreaMarker({ lat, lng, needsReview, onClick }: AreaMarkerProps) {
  if (!needsReview) return null;
  
  return (
    <AdvancedMarker
      position={{ lat, lng }}
      onClick={onClick}
      title="This area is flagged for human review"
      zIndex={100}
    >
      <div className="bg-amber-500 rounded-full p-1 shadow-lg border-2 border-white transform hover:scale-110 transition-transform cursor-pointer">
        <AlertTriangle className="w-5 h-5 text-white" />
      </div>
    </AdvancedMarker>
  );
}
