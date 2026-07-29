import React from "react";
import { useAreas } from "../../hooks/useAreas";

interface AreaFilterProps {
  areaId: number | null;
  onChange: (areaId: number | null) => void;
}

export function AreaFilter({ areaId, onChange }: AreaFilterProps) {
  const { data: areas } = useAreas();
  const sorted = [...(areas ?? [])].sort((a: any, b: any) => a.name.localeCompare(b.name));

  const selectClass =
    "h-9 px-3 text-sm border border-slate-700 rounded-lg bg-slate-800 text-slate-100 " +
    "focus:outline-none focus:ring-2 focus:ring-violet-500 focus:border-violet-500 " +
    "hover:border-slate-600 transition-colors cursor-pointer";

  return (
    <div className="flex items-center gap-2">
      <span className="text-xs font-medium text-slate-500">Area</span>
      <select
        value={areaId ?? ""}
        onChange={(e) => onChange(e.target.value ? Number(e.target.value) : null)}
        className={selectClass}
      >
        <option value="">All areas</option>
        {sorted.map((a: any) => (
          <option key={a.id} value={a.id}>
            {a.name}
          </option>
        ))}
      </select>
    </div>
  );
}
