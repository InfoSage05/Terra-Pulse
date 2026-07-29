import React from "react";
import { PriceRangeFilter } from "./PriceRangeFilter";
import { AreaFilter } from "./AreaFilter";
import { SoldDateFilter } from "./SoldDateFilter";
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
    <div className="px-5 py-3 bg-slate-950 border-b border-slate-800 flex flex-wrap items-center gap-3">
      <PriceRangeFilter
        minPrice={filters.minPrice}
        maxPrice={filters.maxPrice}
        onChange={(f) => onFiltersChange(f)}
      />
      <div className="w-px h-6 bg-slate-800" />
      <AreaFilter
        areaId={filters.areaId}
        onChange={(areaId) => onFiltersChange({ areaId })}
      />
      <div className="w-px h-6 bg-slate-800" />
      <SoldDateFilter
        soldAfter={filters.soldAfter}
        soldBefore={filters.soldBefore}
        onChange={(f) => onFiltersChange(f)}
      />
      <div className="w-px h-6 bg-slate-800" />
      <SortControl value={sortBy} onChange={onSortChange} />
    </div>
  );
}
