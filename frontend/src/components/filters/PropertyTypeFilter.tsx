import React from "react";
import type { PropertyType } from "../../data/mockData";

interface PropertyTypeFilterProps {
  value: PropertyType | null;
  onChange: (t: PropertyType | null) => void;
}

const TYPES: (PropertyType | null)[] = [null, "Apartment", "Terraced", "Semi-Detached", "Detached"];

export function PropertyTypeFilter({ value, onChange }: PropertyTypeFilterProps) {
  return (
    <div className="flex items-center gap-2">
      <span className="text-xs text-gray-500 font-medium">Type</span>
      <select
        value={value || ""}
        onChange={(e) => onChange((e.target.value as PropertyType) || null)}
        className="px-2 py-1 text-xs border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-indigo-400 focus:border-indigo-400 bg-white"
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
