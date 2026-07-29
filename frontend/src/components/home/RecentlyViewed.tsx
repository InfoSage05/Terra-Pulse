import React from "react";
import { useRecentlyViewed } from "../../hooks/useRecentlyViewed";
import { PropertyCard } from "../shared/PropertyCard";

export function RecentlyViewed() {
  const { items, clear } = useRecentlyViewed();

  if (items.length === 0) return null;

  return (
    <section className="max-w-6xl mx-auto px-6 py-12">
      <div className="flex items-center justify-between mb-4">
        <h2 className="font-display text-xl font-semibold text-slate-50">Recently viewed</h2>
        <button
          onClick={clear}
          className="text-xs font-medium text-slate-500 hover:text-slate-300 transition-colors"
        >
          Clear history
        </button>
      </div>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
        {items.map((property) => (
          <PropertyCard key={property.id} property={property} variant="compact" />
        ))}
      </div>
    </section>
  );
}
