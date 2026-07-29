import React from "react";
import { AreaScoreOutput } from "../../types/api";
import { ScorePill, ScorePillType } from "../shared/ScorePill";
import { EmptyScoreState } from "../shared/EmptyScoreState";

export function ScoreSummaryCard({ scores }: { scores: AreaScoreOutput }) {
  const renderScore = (label: string, score: number | null, type: ScorePillType, versionKey: string) => {
    const version = scores.model_versions_used[versionKey];

    return (
      <div className="flex flex-col p-3 border border-slate-700 rounded-lg bg-slate-800/50">
        <span className="text-xs text-slate-500 uppercase font-sans font-semibold tracking-wide mb-2">
          {label}
        </span>
        {score !== null ? (
          <ScorePill score={score} type={type} />
        ) : (
          <EmptyScoreState scoreName={label} />
        )}
        {version && (
          <span className="text-xs text-slate-500 mt-2 font-mono" title="Model Version">
            v: {version}
          </span>
        )}
      </div>
    );
  };

  return (
    <div className="grid grid-cols-2 gap-3 mt-4">
      {renderScore("Affordability", scores.affordability_score, "affordability", "affordability_score")}
      {renderScore("Safety", scores.safety_score, "safety", "safety_score")}
      {renderScore("Livability", scores.livability_score, "livability", "livability_score")}

      <div className="flex flex-col p-3 border border-slate-700 rounded-lg bg-slate-800/50">
        <span className="text-xs text-slate-500 uppercase font-sans font-semibold tracking-wide">
          Last Updated
        </span>
        <span className="text-sm font-medium mt-2 text-slate-200 font-mono">
          {new Date(scores.last_updated).toLocaleDateString()}
        </span>
        {scores.livability_confidence !== null && (
          <span className="text-xs text-slate-400 mt-1 font-mono">
            Confidence: {(scores.livability_confidence * 100).toFixed(0)}%
          </span>
        )}
      </div>
    </div>
  );
}
