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
    <div className="px-5 pt-4 pb-3 border-b border-slate-800 bg-slate-950">
      <div className="flex items-center gap-2">
        <Search className="w-4 h-4 text-slate-500" />
        <span className="text-sm font-medium text-slate-300">
          {propertyCount.toLocaleString()} properties found
        </span>
        {hasActiveFilters && (
          <button
            onClick={onClearFilters}
            className="ml-auto text-xs text-violet-400 hover:text-violet-300 font-medium"
          >
            Clear all filters
          </button>
        )}
        {onAskAI && (
          <button
            onClick={onAskAI}
            className={`flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold text-violet-300 bg-violet-500/10 rounded-lg hover:bg-violet-500/20 transition-colors ${hasActiveFilters ? "" : "ml-auto"}`}
            aria-label="Ask AI assistant"
          >
            <Sparkles className="w-3.5 h-3.5" aria-hidden="true" />
            Ask AI
          </button>
        )}
      </div>
    </div>
  );
}
