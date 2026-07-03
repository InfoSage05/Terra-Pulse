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
    <div className="px-4 py-3 flex justify-center">
      <button
        onClick={onLoadMore}
        className="flex items-center gap-2 px-6 py-2 bg-white border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50 hover:border-gray-400 transition-colors shadow-sm"
      >
        Load more properties
        <ChevronDown className="w-4 h-4" />
      </button>
    </div>
  );
}
