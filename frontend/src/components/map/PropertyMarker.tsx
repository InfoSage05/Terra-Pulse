import React from "react";
import { AdvancedMarker } from "@vis.gl/react-google-maps";
import type { MockProperty } from "../../data/mockData";

function formatPrice(price: number): string {
  if (price >= 1_000_000) return `€${(price / 1_000_000).toFixed(1)}M`;
  return `€${Math.round(price / 1_000)}K`;
}

interface PropertyMarkerProps {
  property: MockProperty;
  isSelected: boolean;
  zoom: number;
  onClick: () => void;
}

export function PropertyMarker({ property, isSelected, zoom, onClick }: PropertyMarkerProps) {
  // Always show price labels — this is the core Zillow-style pattern
  const showLabel = zoom >= 11;

  const baseClasses =
    "flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-bold " +
    "shadow-md border-2 cursor-pointer transition-all duration-150 " +
    "whitespace-nowrap select-none";

  const styleClasses = isSelected
    ? "bg-gray-900 text-white border-gray-900 scale-110 shadow-lg z-10"
    : "bg-white text-gray-900 border-gray-300 hover:scale-105 hover:shadow-lg hover:border-gray-400";

  return (
    <AdvancedMarker
      position={{ lat: property.lat, lng: property.lng }}
      onClick={onClick}
      zIndex={isSelected ? 10 : 1}
    >
      <div className={`${baseClasses} ${styleClasses}`}>
        {showLabel && <span>{formatPrice(property.price_eur)}</span>}
        {showLabel && property.needs_human_review && (
          <span className="flex items-center text-amber-500 ml-0.5">
            <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
              <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
              <line x1="12" y1="9" x2="12" y2="13"/>
              <line x1="12" y1="17" x2="12.01" y2="17"/>
            </svg>
          </span>
        )}
        {!showLabel && (
          <div className={`w-3 h-3 rounded-full ${isSelected ? "bg-white" : "bg-indigo-600"}`} />
        )}
      </div>
    </AdvancedMarker>
  );
}
