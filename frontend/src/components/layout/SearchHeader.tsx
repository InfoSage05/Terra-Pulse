import React from "react";
import { Search, SlidersHorizontal } from "lucide-react";

interface SearchHeaderProps {
  propertyCount: number;
  onClearFilters: () => void;
  hasActiveFilters: boolean;
}

export function SearchHeader({ propertyCount, onClearFilters, hasActiveFilters }: SearchHeaderProps) {
  return (
    <div className="px-4 py-3 border-b border-gray-200 bg-white">
      <div className="flex items-center gap-2 mb-2">
        <Search className="w-4 h-4 text-gray-400" />
        <span className="text-sm font-medium text-gray-700">
          {propertyCount.toLocaleString()} properties found
        </span>
        {hasActiveFilters && (
          <button
            onClick={onClearFilters}
            className="ml-auto text-xs text-indigo-600 hover:text-indigo-800 font-medium"
          >
            Clear all filters
          </button>
        )}
      </div>
    </div>
  );
}
