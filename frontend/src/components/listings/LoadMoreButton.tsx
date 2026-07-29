import React from "react";
import { ChevronDown } from "lucide-react";

interface LoadMoreButtonProps {
  page: number;
  totalPages: number;
  onLoadMore: () => void;
}

export function LoadMoreButton({ page, totalPages, onLoadMore }: LoadMoreButtonProps) {
  if (page >= totalPages - 1) return null;

  return (
    <div className="px-5 py-4 flex justify-center">
      <button
        onClick={onLoadMore}
        className="flex items-center gap-2 px-6 py-2.5 bg-slate-800 border border-slate-700 rounded-lg text-sm font-medium text-slate-200 hover:bg-slate-700 hover:border-slate-600 transition-colors shadow-sm"
      >
        Load more properties
        <ChevronDown className="w-4 h-4" />
      </button>
    </div>
  );
}
