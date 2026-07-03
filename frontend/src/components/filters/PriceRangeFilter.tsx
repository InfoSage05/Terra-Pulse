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

  return (
    <div className="flex items-center gap-2">
      <span className="text-xs text-gray-500 font-medium">Price</span>
      <input
        type="number"
        placeholder="Min"
        value={minStr}
        onChange={(e) => { setMinStr(e.target.value); emit(e.target.value, maxStr); }}
        className="w-20 px-2 py-1 text-xs border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-indigo-400 focus:border-indigo-400"
      />
      <span className="text-xs text-gray-400">–</span>
      <input
        type="number"
        placeholder="Max"
        value={maxStr}
        onChange={(e) => { setMaxStr(e.target.value); emit(minStr, e.target.value); }}
        className="w-20 px-2 py-1 text-xs border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-indigo-400 focus:border-indigo-400"
      />
    </div>
  );
}
