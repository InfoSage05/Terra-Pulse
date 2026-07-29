import React from "react";
import { useCountUp } from "../../hooks/useCountUp";

export type ScorePillType = "safety" | "livability" | "price" | "affordability";

const LABELS: Record<ScorePillType, string> = {
  safety: "Safety",
  livability: "Livability",
  price: "Price",
  affordability: "Affordability",
};

function scoreBand(score: number): "high" | "mid" | "low" {
  if (score >= 75) return "high";
  if (score >= 50) return "mid";
  return "low";
}

const BAND_STYLES: Record<"high" | "mid" | "low", { border: string; text: string }> = {
  high: { border: "border-l-emerald-400", text: "text-emerald-400" },
  mid: { border: "border-l-amber-400", text: "text-amber-400" },
  low: { border: "border-l-rose-500", text: "text-rose-500" },
};

interface ScorePillProps {
  score: number;
  type: ScorePillType;
  size?: "sm" | "md";
}

export function ScorePill({ score, type, size = "md" }: ScorePillProps) {
  const animated = useCountUp(score, 800);
  const band = scoreBand(score);
  const { border, text } = BAND_STYLES[band];
  const label = LABELS[type];

  const sizeClasses =
    size === "sm" ? "px-2 py-1 gap-1.5 text-[11px]" : "px-3 py-1.5 gap-2 text-xs";
  const numberSizeClasses = size === "sm" ? "text-sm" : "text-base";

  return (
    <div
      role="img"
      aria-label={`${label} score ${score.toFixed(0)} out of 100`}
      className={`inline-flex items-center border-l-4 ${border} bg-slate-800 rounded-r-md ${sizeClasses}`}
    >
      <span className="font-sans font-medium uppercase tracking-wide text-slate-400">
        {label}
      </span>
      <span className={`font-mono font-semibold ${numberSizeClasses} ${text}`}>
        {animated.toFixed(0)}
      </span>
    </div>
  );
}
