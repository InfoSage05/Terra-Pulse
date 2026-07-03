import React from "react";
import { AlertTriangle } from "lucide-react";
import { MockProperty, AREA_SCORES_MOCK } from "../../data/mockData";
import { scoreColor } from "../../lib/theme";

interface PropertyCardProps {
  property: MockProperty;
  isSelected: boolean;
  onClick: () => void;
}

export function PropertyCard({ property, isSelected, onClick }: PropertyCardProps) {
  const scores = AREA_SCORES_MOCK[property.area_id];

  const typeColors: Record<string, string> = {
    Detached: "bg-blue-50 text-blue-700 border border-blue-200",
    "Semi-Detached": "bg-emerald-50 text-emerald-700 border border-emerald-200",
    Terraced: "bg-violet-50 text-violet-700 border border-violet-200",
    Apartment: "bg-amber-50 text-amber-700 border border-amber-200",
  };

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
        <span
          className={`text-xs font-semibold px-2.5 py-1 rounded-full whitespace-nowrap ${
            typeColors[property.property_type] || "bg-gray-100 text-gray-700 border border-gray-200"
          }`}
        >
          {property.property_type}
        </span>
      </div>

      <p className="text-sm text-gray-700 mb-1">{property.address_raw}</p>
      <p className="text-xs text-gray-400 mb-3">
        {property.area_name} · Sold {new Date(property.sale_date).toLocaleDateString("en-IE", { month: "short", year: "numeric" })}
      </p>

      {scores && (
        <div className="flex items-center gap-4 text-xs">
          <span className="text-gray-500">
            Safety <span className="font-bold" style={{ color: scoreColor(scores.safety) }}>{scores.safety ?? "—"}</span>
          </span>
          <span className="text-gray-500">
            Afford. <span className="font-bold" style={{ color: scoreColor(scores.affordability) }}>{scores.affordability ?? "—"}</span>
          </span>
          <span className="text-gray-500">
            Live. <span className="font-bold" style={{ color: scoreColor(scores.livability) }}>{scores.livability ?? "—"}</span>
          </span>
          {(scores.needs_human_review || property.needs_human_review) && (
            <span className="flex items-center gap-1 text-amber-600 font-medium ml-auto bg-amber-50 px-2 py-0.5 rounded-full">
              <AlertTriangle className="w-3 h-3" />
              Review
            </span>
          )}
        </div>
      )}
    </div>
  );
}
