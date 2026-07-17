import React from "react";
import { PriceRangeFilter } from "./PriceRangeFilter";
import { SortControl } from "./SortControl";
import { FilterState, SortOption } from "../../hooks/useSearchState";

interface FilterBarProps {
  filters: FilterState;
  sortBy: SortOption;
  onFiltersChange: (f: Partial<FilterState>) => void;
  onSortChange: (s: SortOption) => void;
}

export function FilterBar({ filters, sortBy, onFiltersChange, onSortChange }: FilterBarProps) {
  return (
    <div className="px-5 py-3 bg-white border-b border-gray-200 flex flex-wrap items-center gap-3">
      <PriceRangeFilter
        minPrice={filters.minPrice}
        maxPrice={filters.maxPrice}
        onChange={(f) => onFiltersChange(f)}
      />
      <div className="w-px h-6 bg-gray-200" />
      <SortControl value={sortBy} onChange={onSortChange} />
    </div>
  );
}
