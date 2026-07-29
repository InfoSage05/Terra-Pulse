import React, { useMemo } from "react";
import { Marker, Popup } from "react-leaflet";
import L from "leaflet";
import { PropertyListing } from "../../types/api";
import { isRecentSale } from "../../lib/recency";

function formatPrice(price: number): string {
  if (price >= 1_000_000) return `€${(price / 1_000_000).toFixed(1)}M`;
  return `€${Math.round(price / 1_000)}K`;
}

interface PropertyMarkerProps {
  property: PropertyListing;
  isSelected: boolean;
  zoom: number;
  onClick: () => void;
  /** True when `property.lat`/`lon` are a jittered area-centroid fallback
   *  (the PPR dataset this app runs on doesn't include per-property
   *  geocoding), not the real house location - rendered with a dashed
   *  ring so it's never mistaken for a precise pin. */
  approximate?: boolean;
}

export function PropertyMarker({ property, isSelected, zoom, onClick, approximate }: PropertyMarkerProps) {
  const showLabel = zoom >= 11;
  const recent = isRecentSale(property.sale_date);

  const icon = useMemo(() => {
    const dotColor = isSelected ? "#fff" : recent ? "#34d399" : "#fb7185";
    const ringColor = isSelected ? "#8b5cf6" : recent ? "#10b981" : "#f43f5e";
    const border = approximate ? `2px dashed ${ringColor}` : `2px solid ${isSelected ? "#8b5cf6" : "transparent"}`;

    const selectedClasses = isSelected
      ? "background:#8b5cf6;color:#fff;border-color:#8b5cf6;box-shadow:0 4px 12px rgba(139,92,246,0.5);"
      : `background:#1e293b;color:#e2e8f0;border-color:${ringColor};`;

    const html = showLabel
      ? `<div style="display:flex;align-items:center;padding:3px 10px;border-radius:9999px;
           font:600 11px 'JetBrains Mono',monospace;white-space:nowrap;
           border:2px ${approximate ? "dashed" : "solid"};
           ${selectedClasses}">${formatPrice(property.price_eur)}</div>`
      : `<div style="width:12px;height:12px;border-radius:9999px;
           background:${dotColor};border:${border};"></div>`;

    return L.divIcon({
      className: "",
      html,
      iconSize: showLabel ? undefined : [12, 12],
      iconAnchor: showLabel ? [30, 12] : [6, 6],
    });
  }, [isSelected, showLabel, property.price_eur, recent, approximate]);

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
        <p className="text-xs text-slate-500">
          {recent ? "Sold within the last 90 days" : "Sold more than 90 days ago"}
        </p>
        {approximate && (
          <p className="text-xs text-amber-600 mt-1">Approximate location (area-level, not the exact address)</p>
        )}
      </Popup>
    </Marker>
  );
}
