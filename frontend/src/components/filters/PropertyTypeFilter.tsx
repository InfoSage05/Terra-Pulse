import React from "react";
import type { PropertyType } from "../../data/mockData";

interface PropertyTypeFilterProps {
  value: PropertyType | null;
  onChange: (t: PropertyType | null) => void;
}

export function PropertyTypeFilter({ value, onChange }: PropertyTypeFilterProps) {
  const selectClass =
    "h-9 px-3 text-sm border border-gray-300 rounded-lg bg-white " +
    "focus:outline-none focus:ring-2 focus:ring-indigo-400 focus:border-indigo-400 " +
    "hover:border-gray-400 transition-colors cursor-pointer";

  return (
    <div className="flex items-center gap-2">
      <span className="text-xs font-medium text-gray-500">Type</span>
      <select
        value={value || ""}
        onChange={(e) => onChange((e.target.value as PropertyType) || null)}
        className={selectClass}
      >
        <option value="">All types</option>
        <option value="Apartment">Apartment</option>
        <option value="Terraced">Terraced</option>
        <option value="Semi-Detached">Semi-Detached</option>
        <option value="Detached">Detached</option>
      </select>
    </div>
  );
}
