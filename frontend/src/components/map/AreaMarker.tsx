import React from "react";
import { Marker, Popup } from "react-leaflet";
import L from "leaflet";
import { renderToString } from "react-dom/server";
import { AlertTriangle } from "lucide-react";

interface AreaMarkerProps {
  lat: number;
  lng: number;
  needsReview: boolean;
  onClick: () => void;
}

export function AreaMarker({ lat, lng, needsReview, onClick }: AreaMarkerProps) {
  if (!needsReview) return null;
  
  // Create a custom icon using a React component rendered to HTML
  const iconHtml = renderToString(
    <div className="bg-amber-500 rounded-full p-1 shadow-lg border-2 border-white transform hover:scale-110 transition-transform cursor-pointer flex items-center justify-center">
      <AlertTriangle className="w-5 h-5 text-white" />
    </div>
  );

  const customIcon = L.divIcon({
    html: iconHtml,
    className: "", // Remove default leaflet class to avoid background styling
    iconSize: [32, 32],
    iconAnchor: [16, 16],
  });

  return (
    <Marker
      position={[lat, lng]}
      icon={customIcon}
      eventHandlers={{
        click: onClick,
      }}
    >
      <Popup>This area is flagged for human review</Popup>
    </Marker>
  );
}
