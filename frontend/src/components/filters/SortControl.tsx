import React from "react";
import type { SortOption } from "../../data/mockData";

interface SortControlProps {
  value: SortOption;
  onChange: (s: SortOption) => void;
}

const OPTIONS: { value: SortOption; label: string }[] = [
  { value: "price_asc", label: "Price: Low to High" },
  { value: "price_desc", label: "Price: High to Low" },
  { value: "recent", label: "Most Recent" },
  { value: "score", label: "Livability Score" },
];

export function SortControl({ value, onChange }: SortControlProps) {
  const selectClass =
    "h-9 px-3 text-sm border border-gray-300 rounded-lg bg-white " +
    "focus:outline-none focus:ring-2 focus:ring-indigo-400 focus:border-indigo-400 " +
    "hover:border-gray-400 transition-colors cursor-pointer";

  return (
    <div className="flex items-center gap-2">
      <span className="text-xs font-medium text-gray-500">Sort</span>
      <select
        value={value}
        onChange={(e) => onChange(e.target.value as SortOption)}
        className={selectClass}
      >
        {OPTIONS.map((o) => (
          <option key={o.value} value={o.value}>{o.label}</option>
        ))}
      </select>
    </div>
  );
}
