import React from "react";
import { PropertyListing } from "../../types/api";

interface PropertyCardProps {
  property: PropertyListing;
  isSelected: boolean;
  onClick: () => void;
}

export function PropertyCard({ property, isSelected, onClick }: PropertyCardProps) {
  return (
    <div
      onClick={onClick}
      className={`px-5 py-4 cursor-pointer transition-all duration-150 border-b border-slate-800 ${
        isSelected
          ? "bg-violet-500/10 border-l-4 border-l-violet-500"
          : "hover:bg-slate-800/60 border-l-4 border-l-transparent"
      }`}
    >
      <div className="flex items-start justify-between mb-1.5">
        <span className="text-xl font-mono font-bold tracking-tight text-slate-50">
          €{property.price_eur.toLocaleString("en-IE")}
        </span>
      </div>

      <p className="text-sm text-slate-300 mb-1">{property.address_raw}</p>
      <p className="text-xs text-slate-500">
        {property.area_name || `Area #${property.area_id}`} · Sold{" "}
        {new Date(property.sale_date).toLocaleDateString("en-IE", {
          month: "short",
          year: "numeric",
        })}
      </p>
    </div>
  );
}
