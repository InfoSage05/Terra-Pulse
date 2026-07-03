import React, { useState } from "react";
import { AdvancedMarker, InfoWindow } from "@vis.gl/react-google-maps";
import { AlertTriangle } from "lucide-react";

interface AreaMarkerProps {
  position: google.maps.LatLngLiteral;
  needsReview: boolean;
  onClick: () => void;
}

export function AreaMarker({ position, needsReview, onClick }: AreaMarkerProps) {
  const [infoOpen, setInfoOpen] = useState(false);

  if (!needsReview) return null;

  return (
    <AdvancedMarker
      position={position}
      onClick={() => {
        setInfoOpen(true);
        onClick();
      }}
    >
      <div className="bg-amber-500 rounded-full p-1.5 shadow-lg border-2 border-white cursor-pointer hover:scale-110 transition-transform flex items-center justify-center">
        <AlertTriangle className="w-5 h-5 text-white" />
      </div>

      {infoOpen && (
        <InfoWindow
          position={position}
          onClose={() => setInfoOpen(false)}
        >
          <p className="text-sm text-amber-800 whitespace-nowrap">
            This area is flagged for human review
          </p>
        </InfoWindow>
      )}
    </AdvancedMarker>
  );
}
