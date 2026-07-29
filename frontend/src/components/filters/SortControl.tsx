import React from "react";
import { SortOption } from "../../hooks/useSearchState";

interface SortControlProps {
  value: SortOption;
  onChange: (s: SortOption) => void;
}

const OPTIONS: { value: SortOption; label: string }[] = [
  { value: "price_asc", label: "Price: Low to High" },
  { value: "price_desc", label: "Price: High to Low" },
  { value: "recent", label: "Most Recent" },
];

export function SortControl({ value, onChange }: SortControlProps) {
  const selectClass =
    "h-9 px-3 text-sm border border-slate-700 rounded-lg bg-slate-800 text-slate-100 " +
    "focus:outline-none focus:ring-2 focus:ring-violet-500 focus:border-violet-500 " +
    "hover:border-slate-600 transition-colors cursor-pointer";

  return (
    <div className="flex items-center gap-2">
      <span className="text-xs font-medium text-slate-500">Sort</span>
      <select
        value={value}
        onChange={(e) => onChange(e.target.value as SortOption)}
        className={selectClass}
      >
        {OPTIONS.map((o) => (
          <option key={o.value} value={o.value}>
            {o.label}
          </option>
        ))}
      </select>
    </div>
  );
}
