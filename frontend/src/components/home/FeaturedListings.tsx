import React, { useMemo } from "react";
import { useProperties } from "../../hooks/useProperties";
import { useAreaScoresMap } from "../../hooks/useAreaScoresMap";
import { PropertyCard } from "../shared/PropertyCard";
import { Loader2 } from "lucide-react";

export function FeaturedListings() {
  // TODO: wire a dedicated GET /v1/properties/featured (or sort_by=recency)
  // endpoint once one exists — for now this reuses the real, generic listings
  // endpoint with a small limit, which is the closest real equivalent.
  const { data, isLoading } = useProperties({ limit: 6, sort_by: "recent" });
  const properties = data?.items;

  const areaIds = useMemo(
    () => Array.from(new Set((properties ?? []).map((p) => p.area_id).filter(Boolean))),
    [properties]
  );
  const scores = useAreaScoresMap(areaIds);

  if (isLoading) {
    return (
      <section className="max-w-6xl mx-auto px-6 py-12">
        <div className="flex items-center justify-center py-16">
          <Loader2 className="w-6 h-6 text-violet-400 animate-spin" />
        </div>
      </section>
    );
  }

  if (!properties || properties.length === 0) return null;

  return (
    <section className="max-w-6xl mx-auto px-6 py-12">
      <p className="font-mono text-xs font-semibold text-violet-400 uppercase tracking-widest mb-2">
        Featured
      </p>
      <h2 className="font-display text-2xl md:text-3xl font-semibold text-slate-50 mb-6">
        Handpicked for you
      </h2>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {properties.map((property, i) => (
          <PropertyCard
            key={property.id}
            property={property}
            isNew={i < 2}
            needsReview={scores[property.area_id]?.needs_human_review}
          />
        ))}
      </div>
    </section>
  );
}
