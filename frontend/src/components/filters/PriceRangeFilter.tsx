import React, { useState, useEffect, useRef } from "react";

interface PriceRangeFilterProps {
  minPrice: number | null;
  maxPrice: number | null;
  onChange: (f: { minPrice: number | null; maxPrice: number | null }) => void;
}

export function PriceRangeFilter({ minPrice, maxPrice, onChange }: PriceRangeFilterProps) {
  const [minStr, setMinStr] = useState(minPrice ? String(minPrice) : "");
  const [maxStr, setMaxStr] = useState(maxPrice ? String(maxPrice) : "");
  const debounce = useRef<ReturnType<typeof setTimeout>>();

  useEffect(() => {
    setMinStr(minPrice ? String(minPrice) : "");
    setMaxStr(maxPrice ? String(maxPrice) : "");
  }, [minPrice, maxPrice]);

  const emit = (min: string, max: string) => {
    clearTimeout(debounce.current);
    debounce.current = setTimeout(() => {
      onChange({
        minPrice: min ? Number(min) : null,
        maxPrice: max ? Number(max) : null,
      });
    }, 400);
  };

  const inputClass =
    "w-24 h-9 px-3 text-sm border border-gray-300 rounded-lg bg-white " +
    "focus:outline-none focus:ring-2 focus:ring-indigo-400 focus:border-indigo-400 " +
    "hover:border-gray-400 transition-colors";

  return (
    <div className="flex items-center gap-2">
      <span className="text-xs font-medium text-gray-500">Price</span>
      <input
        type="number"
        placeholder="Min €"
        value={minStr}
        onChange={(e) => { setMinStr(e.target.value); emit(e.target.value, maxStr); }}
        className={inputClass}
      />
      <span className="text-xs text-gray-400">–</span>
      <input
        type="number"
        placeholder="Max €"
        value={maxStr}
        onChange={(e) => { setMaxStr(e.target.value); emit(minStr, e.target.value); }}
        className={inputClass}
      />
    </div>
  );
}
