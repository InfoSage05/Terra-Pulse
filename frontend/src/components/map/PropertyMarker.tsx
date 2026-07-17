import React, { useMemo } from "react";
import { Marker, Popup } from "react-leaflet";
import L from "leaflet";
import { PropertyListing } from "../../types/api";

function formatPrice(price: number): string {
  if (price >= 1_000_000) return `€${(price / 1_000_000).toFixed(1)}M`;
  return `€${Math.round(price / 1_000)}K`;
}

interface PropertyMarkerProps {
  property: PropertyListing;
  isSelected: boolean;
  zoom: number;
  onClick: () => void;
}

export function PropertyMarker({ property, isSelected, zoom, onClick }: PropertyMarkerProps) {
  const showLabel = zoom >= 11;

  const icon = useMemo(() => {
    const selectedClasses = isSelected
      ? "background:#8b5cf6;color:#fff;border-color:#8b5cf6;box-shadow:0 4px 12px rgba(139,92,246,0.5);"
      : "background:#1e293b;color:#e2e8f0;border-color:#334155;";

    const html = showLabel
      ? `<div style="display:flex;align-items:center;padding:3px 10px;border-radius:9999px;
           font:600 11px 'JetBrains Mono',monospace;white-space:nowrap;border:2px solid;
           ${selectedClasses}">${formatPrice(property.price_eur)}</div>`
      : `<div style="width:12px;height:12px;border-radius:9999px;
           background:${isSelected ? "#fff" : "#8b5cf6"};border:2px solid ${isSelected ? "#8b5cf6" : "transparent"};"></div>`;

    return L.divIcon({
      className: "",
      html,
      iconSize: showLabel ? undefined : [12, 12],
      iconAnchor: showLabel ? [30, 12] : [6, 6],
    });
  }, [isSelected, showLabel, property.price_eur]);

  if (!property.lat || !property.lon) return null;

  return (
    <Marker
      position={[property.lat, property.lon]}
      icon={icon}
      zIndexOffset={isSelected ? 1000 : 0}
      eventHandlers={{ click: onClick }}
    >
      <Popup>
        <p className="text-sm font-mono font-semibold">{formatPrice(property.price_eur)}</p>
        <p className="text-xs text-slate-500">{property.address_raw}</p>
      </Popup>
    </Marker>
  );
}
