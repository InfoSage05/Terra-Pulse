import React from "react";
import { AdvancedMarker } from "@vis.gl/react-google-maps";
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
  if (!property.lat || !property.lon) return null;

  const baseClasses =
    "flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-bold " +
    "shadow-md border-2 cursor-pointer transition-all duration-150 " +
    "whitespace-nowrap select-none";

  const styleClasses = isSelected
    ? "bg-gray-900 text-white border-gray-900 scale-110 shadow-lg z-10"
    : "bg-white text-gray-900 border-gray-300 hover:scale-105 hover:shadow-lg hover:border-gray-400";

  return (
    <AdvancedMarker
      position={{ lat: property.lat!, lng: property.lon! }}
      onClick={onClick}
      zIndex={isSelected ? 10 : 1}
    >
      <div className={`${baseClasses} ${styleClasses}`}>
        {showLabel && <span>{formatPrice(property.price_eur)}</span>}
        {!showLabel && (
          <div className={`w-3 h-3 rounded-full ${isSelected ? "bg-white" : "bg-indigo-600"}`} />
        )}
      </div>
    </AdvancedMarker>
  );
}
