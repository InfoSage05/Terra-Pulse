import React from "react";
import { Search, Sparkles } from "lucide-react";

interface SearchHeaderProps {
  propertyCount: number;
  onClearFilters: () => void;
  hasActiveFilters: boolean;
  onAskAI?: () => void;
}

export function SearchHeader({ propertyCount, onClearFilters, hasActiveFilters, onAskAI }: SearchHeaderProps) {
  return (
    <div className="px-5 pt-4 pb-3 border-b border-gray-100 bg-white">
      <div className="flex items-center gap-2">
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
        {onAskAI && (
          <button
            onClick={onAskAI}
            className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold text-indigo-600 bg-indigo-50 rounded-lg hover:bg-indigo-100 transition-colors"
          >
            <Sparkles className="w-3.5 h-3.5" />
            Ask AI
          </button>
        )}
      </div>
    </div>
  );
}
