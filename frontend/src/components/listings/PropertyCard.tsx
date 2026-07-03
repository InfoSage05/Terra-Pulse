import React from "react";
import { AlertTriangle } from "lucide-react";
import { MockProperty, AREA_SCORES_MOCK } from "../../data/mockData";

interface PropertyCardProps {
  property: MockProperty;
  isSelected: boolean;
  onClick: () => void;
}

export function PropertyCard({ property, isSelected, onClick }: PropertyCardProps) {
  const scores = AREA_SCORES_MOCK[property.area_id];

  const typeColors: Record<string, string> = {
    Detached: "bg-blue-100 text-blue-800",
    "Semi-Detached": "bg-green-100 text-green-800",
    Terraced: "bg-purple-100 text-purple-800",
    Apartment: "bg-amber-100 text-amber-800",
  };

  return (
    <div
      onClick={onClick}
      className={`px-4 py-3 border-b border-gray-100 cursor-pointer transition-colors hover:bg-gray-50 ${
        isSelected ? "bg-indigo-50 border-l-4 border-l-indigo-500" : ""
      }`}
    >
      <div className="flex items-start justify-between mb-1">
        <span className="text-lg font-bold text-gray-900">
          €{property.price_eur.toLocaleString()}
        </span>
        <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${typeColors[property.property_type] || "bg-gray-100 text-gray-700"}`}>
          {property.property_type}
        </span>
      </div>

      <p className="text-sm text-gray-700 mb-1">{property.address_raw}</p>
      <p className="text-xs text-gray-400 mb-2">
        {property.area_name} · Sold {new Date(property.sale_date).toLocaleDateString("en-IE", { month: "short", year: "numeric" })}
      </p>

      {scores && (
        <div className="flex items-center gap-3 text-xs text-gray-500">
          <span>
            Safety <span className="font-medium text-gray-700">{scores.safety ?? "—"}</span>
          </span>
          <span>
            Afford. <span className="font-medium text-gray-700">{scores.affordability ?? "—"}</span>
          </span>
          <span>
            Live. <span className="font-medium text-gray-700">{scores.livability ?? "—"}</span>
          </span>
          {(scores.needs_human_review || property.needs_human_review) && (
            <span className="flex items-center gap-1 text-amber-600 ml-auto">
              <AlertTriangle className="w-3 h-3" />
              Review
            </span>
          )}
        </div>
      )}
    </div>
  );
}
