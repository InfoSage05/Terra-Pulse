import React from "react";
import { PriceRangeFilter } from "./PriceRangeFilter";
import { PropertyTypeFilter } from "./PropertyTypeFilter";
import { SortControl } from "./SortControl";
import type { FilterState, SortOption, PropertyType } from "../../data/mockData";

interface FilterBarProps {
  filters: FilterState;
  sortBy: SortOption;
  onFiltersChange: (f: Partial<FilterState>) => void;
  onSortChange: (s: SortOption) => void;
}

export function FilterBar({ filters, sortBy, onFiltersChange, onSortChange }: FilterBarProps) {
  return (
    <div className="px-4 py-2 bg-white border-b border-gray-200 flex flex-wrap items-center gap-3">
      <PriceRangeFilter
        minPrice={filters.minPrice}
        maxPrice={filters.maxPrice}
        onChange={(f) => onFiltersChange(f)}
      />
      <div className="w-px h-5 bg-gray-200" />
      <PropertyTypeFilter
        value={filters.propertyType}
        onChange={(t) => onFiltersChange({ propertyType: t })}
      />
      <div className="w-px h-5 bg-gray-200" />
      <SortControl value={sortBy} onChange={onSortChange} />
    </div>
  );
}
