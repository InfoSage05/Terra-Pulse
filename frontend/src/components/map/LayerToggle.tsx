import React from "react";
import { ScoreType } from "../../lib/colourScales";

interface LayerToggleProps {
  activeLayer: ScoreType;
  onChange: (layer: ScoreType) => void;
}

export function LayerToggle({ activeLayer, onChange }: LayerToggleProps) {
  const options: { value: ScoreType; label: string }[] = [
    { value: "price", label: "Price" },
    { value: "affordability", label: "Affordability" },
    { value: "safety", label: "Safety" },
    { value: "livability", label: "Livability" },
  ];

  return (
    <div className="absolute top-4 left-4 z-[1000] bg-slate-900/90 backdrop-blur border border-slate-700 rounded-xl p-1 flex gap-1">
      {options.map((opt) => (
        <button
          key={opt.value}
          onClick={() => onChange(opt.value)}
          aria-pressed={activeLayer === opt.value}
          className={`px-3 py-1.5 text-sm font-medium rounded-lg transition-colors ${
            activeLayer === opt.value
              ? "bg-violet-500 text-white"
              : "text-slate-300 hover:bg-slate-800"
          }`}
        >
          {opt.label}
        </button>
      ))}
    </div>
  );
}
