import React from "react";
import { AreaScoreOutput } from "../../types/api";
import { getColorForScore, ScoreType } from "../../lib/colourScales";

export function ScoreSummaryCard({ scores }: { scores: AreaScoreOutput }) {
  const renderScore = (label: string, score: number | null, type: ScoreType, versionKey: string) => {
    const color = getColorForScore(type, score);
    const version = scores.model_versions_used[versionKey];
    
    return (
      <div className="flex flex-col p-3 border rounded-md">
        <span className="text-xs text-gray-500 uppercase font-semibold">{label}</span>
        <div className="mt-1 flex items-baseline">
          {score !== null ? (
            <span className="text-2xl font-bold" style={{ color }}>{score.toFixed(1)}</span>
          ) : (
            <span className="text-sm text-gray-400 italic">Not available</span>
          )}
          {score !== null && <span className="ml-1 text-sm text-gray-500">/ 100</span>}
        </div>
        {version && <span className="text-xs text-gray-400 mt-2 font-mono" title="Model Version">v: {version}</span>}
      </div>
    );
  };

  return (
    <div className="grid grid-cols-2 gap-3 mt-4">
      {renderScore("Affordability", scores.affordability_score, "affordability", "affordability_score")}
      {renderScore("Safety", scores.safety_score, "safety", "safety_score")}
      {renderScore("Livability", scores.livability_score, "livability", "livability_score")}
      
      <div className="flex flex-col p-3 border rounded-md bg-gray-50">
        <span className="text-xs text-gray-500 uppercase font-semibold">Last Updated</span>
        <span className="text-sm font-medium mt-2 text-gray-800">
          {new Date(scores.last_updated).toLocaleDateString()}
        </span>
        {scores.livability_confidence !== null && (
          <span className="text-xs text-gray-500 mt-1">
            Confidence: {(scores.livability_confidence * 100).toFixed(0)}%
          </span>
        )}
      </div>
    </div>
  );
}
