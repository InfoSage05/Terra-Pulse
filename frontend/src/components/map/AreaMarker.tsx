import React, { useState } from "react";
import { Marker, Popup } from "react-leaflet";
import L from "leaflet";

interface AreaMarkerProps {
  position: { lat: number; lng: number };
  needsReview: boolean;
  onClick: () => void;
}

// Inline SVG (lucide "alert-triangle" path) — divIcon content is raw HTML,
// so a React icon component can't be rendered into it directly.
const ALERT_TRIANGLE_SVG = `
  <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="white" stroke-width="2.5"
       stroke-linecap="round" stroke-linejoin="round">
    <path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/>
    <path d="M12 9v4"/>
    <path d="M12 17h.01"/>
  </svg>
`;

// CRITICAL (see general-architecture skill): needs_human_review must surface
// as an unmissable visual warning directly on the map, not just in the side
// panel. The pulsing rose ring (`.area-marker-pulse`, defined in index.css)
// is that unmissable marker.
function buildIcon(): L.DivIcon {
  return L.divIcon({
    className: "",
    html: `
      <div class="area-marker-pulse" style="
        width: 32px; height: 32px; border-radius: 9999px;
        background: #f43f5e; display: flex; align-items: center; justify-content: center;
        border: 2px solid white; cursor: pointer;
      ">
        ${ALERT_TRIANGLE_SVG}
      </div>
    `,
    iconSize: [32, 32],
    iconAnchor: [16, 16],
  });
}

export function AreaMarker({ position, needsReview, onClick }: AreaMarkerProps) {
  const [icon] = useState(buildIcon);

  if (!needsReview) return null;

  return (
    <Marker
      position={[position.lat, position.lng]}
      icon={icon}
      eventHandlers={{ click: onClick }}
    >
      <Popup>
        <p className="text-sm text-rose-600 whitespace-nowrap font-medium">
          This area is flagged for human review
        </p>
      </Popup>
    </Marker>
  );
}
