import React, { useState, useEffect, useRef } from "react";

interface SoldDateFilterProps {
  soldAfter: string | null;
  soldBefore: string | null;
  onChange: (f: { soldAfter: string | null; soldBefore: string | null }) => void;
}

export function SoldDateFilter({ soldAfter, soldBefore, onChange }: SoldDateFilterProps) {
  const [afterStr, setAfterStr] = useState(soldAfter ?? "");
  const [beforeStr, setBeforeStr] = useState(soldBefore ?? "");
  const debounce = useRef<ReturnType<typeof setTimeout> | undefined>(undefined);

  useEffect(() => {
    setAfterStr(soldAfter ?? "");
    setBeforeStr(soldBefore ?? "");
  }, [soldAfter, soldBefore]);

  const emit = (after: string, before: string) => {
    clearTimeout(debounce.current);
    debounce.current = setTimeout(() => {
      onChange({ soldAfter: after || null, soldBefore: before || null });
    }, 400);
  };

  const inputClass =
    "h-9 px-3 text-sm border border-slate-700 rounded-lg bg-slate-800 text-slate-100 " +
    "focus:outline-none focus:ring-2 focus:ring-violet-500 focus:border-violet-500 " +
    "hover:border-slate-600 transition-colors";

  return (
    <div className="flex items-center gap-2">
      <span className="text-xs font-medium text-slate-500">Sold</span>
      <input
        type="date"
        value={afterStr}
        onChange={(e) => { setAfterStr(e.target.value); emit(e.target.value, beforeStr); }}
        className={inputClass}
      />
      <span className="text-xs text-slate-600">–</span>
      <input
        type="date"
        value={beforeStr}
        onChange={(e) => { setBeforeStr(e.target.value); emit(afterStr, e.target.value); }}
        className={inputClass}
      />
    </div>
  );
}
