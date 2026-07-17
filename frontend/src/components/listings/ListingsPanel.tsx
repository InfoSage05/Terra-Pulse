import React, { useRef, useEffect } from "react";
import { PropertyCard } from "./PropertyCard";
import { ListingsCount } from "./ListingsCount";
import { LoadMoreButton } from "./LoadMoreButton";
import { PropertyListing } from "../../types/api";

interface ListingsPanelProps {
  properties: PropertyListing[];
  filteredCount: number;
  page: number;
  totalPages: number;
  selectedPropertyId: number | null;
  onSelectProperty: (id: number) => void;
  onLoadMore: () => void;
}

export function ListingsPanel({
  properties,
  filteredCount,
  page,
  totalPages,
  selectedPropertyId,
  onSelectProperty,
  onLoadMore,
}: ListingsPanelProps) {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (selectedPropertyId && containerRef.current) {
      const el = containerRef.current.querySelector(`[data-property-id="${selectedPropertyId}"]`);
      if (el) {
        el.scrollIntoView({ behavior: "smooth", block: "nearest" });
      }
    }
  }, [selectedPropertyId]);

  return (
    <div className="flex flex-col h-full">
      <ListingsCount total={filteredCount} showing={properties.length} />
      <div ref={containerRef} className="flex-1 overflow-y-auto">
        {properties.map((p) => (
          <div key={p.id} data-property-id={p.id}>
            <PropertyCard
              property={p}
              isSelected={selectedPropertyId === p.id}
              onClick={() => onSelectProperty(p.id)}
            />
          </div>
        ))}
        {properties.length === 0 && (
          <div className="flex items-center justify-center h-48 text-gray-400 text-sm">
            No properties match your filters.
          </div>
        )}
      </div>
      <LoadMoreButton page={page} totalPages={totalPages} onLoadMore={onLoadMore} />
    </div>
  );
}
