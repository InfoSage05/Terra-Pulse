import React from "react";
import { AlertTriangle } from "lucide-react";
import { PropertyListing } from "../../types/api";

interface PropertyCardProps {
  property: PropertyListing;
  isSelected: boolean;
  onClick: () => void;
}

const typeColors: Record<string, string> = {
  Detached: "bg-blue-50 text-blue-700 border border-blue-200",
  "Semi-Detached": "bg-emerald-50 text-emerald-700 border border-emerald-200",
  Terraced: "bg-violet-50 text-violet-700 border border-violet-200",
  Apartment: "bg-amber-50 text-amber-700 border border-amber-200",
};

export function PropertyCard({ property, isSelected, onClick }: PropertyCardProps) {
  const displayType = property.property_type || "Residential";

  return (
    <div
      onClick={onClick}
      className={`px-5 py-4 cursor-pointer transition-all duration-150 border-b border-gray-100 ${
        isSelected
          ? "bg-indigo-50 border-l-4 border-l-indigo-500"
          : "hover:bg-gray-50 hover:shadow-sm border-l-4 border-l-transparent"
      }`}
    >
      <div className="flex items-start justify-between mb-1.5">
        <span className="text-xl font-extrabold tracking-tight text-gray-900">
          €{property.price_eur.toLocaleString()}
        </span>
      </div>

      <p className="text-sm text-gray-700 mb-1">{property.address_raw}</p>
      <p className="text-xs text-gray-400">
        {property.area_name || `Area #${property.area_id}`} · Sold{" "}
        {new Date(property.sale_date).toLocaleDateString("en-IE", {
          month: "short",
          year: "numeric",
        })}
      </p>
    </div>
  );
}
