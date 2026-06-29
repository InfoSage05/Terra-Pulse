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
    <div className="absolute top-4 left-4 bg-white rounded-md shadow-md flex overflow-hidden z-10 border border-gray-200">
      {options.map((opt) => (
        <button
          key={opt.value}
          onClick={() => onChange(opt.value)}
          className={`px-4 py-2 text-sm font-medium transition-colors ${
            activeLayer === opt.value
              ? "bg-indigo-600 text-white"
              : "bg-white text-gray-700 hover:bg-gray-50"
          } ${opt.value !== "livability" ? "border-r border-gray-200" : ""}`}
        >
          {opt.label}
        </button>
      ))}
    </div>
  );
}
