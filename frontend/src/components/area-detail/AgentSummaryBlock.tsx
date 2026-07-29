import React from "react";
import { AreaScoreOutput } from "../../types/api";

export function AgentSummaryBlock({ scores }: { scores: AreaScoreOutput }) {
  if (scores.livability_confidence === null && !scores.agent_summary) {
    return null;
  }

  return (
    <div className="bg-slate-800/50 border border-slate-700 rounded-lg shadow-sm p-4 mt-4">
      <h3 className="text-sm font-sans font-semibold text-slate-300 uppercase tracking-wide mb-3 border-b border-slate-700 pb-2">
        Agent Analysis
      </h3>

      <div className="text-sm text-slate-300 leading-relaxed italic mb-4">
        {scores.agent_summary
          ? `"${scores.agent_summary}"`
          : `"Based on unstructured community discussions, historical news sentiment, and local forums, the qualitative livability of this area is assessed at ${(scores.livability_score || 0).toFixed(1)}/100."`
        }
      </div>

      <div className="flex justify-between items-center text-xs text-slate-500 bg-slate-900/60 p-2 rounded font-mono">
        {scores.livability_confidence !== null && (
          <span>Confidence: {(scores.livability_confidence * 100).toFixed(0)}%</span>
        )}
        <span>Updated: {new Date(scores.last_updated).toLocaleDateString()}</span>
      </div>
    </div>
  );
}
