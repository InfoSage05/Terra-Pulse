import React from "react";
import { AreaScoreOutput } from "../../types/api";

export function AgentSummaryBlock({ scores }: { scores: AreaScoreOutput }) {
  if (scores.livability_confidence === null) {
    return null; // no unstructured pipeline run yet
  }

  return (
    <div className="bg-white border rounded-md shadow-sm p-4 mt-4">
      <h3 className="text-sm font-semibold text-gray-800 uppercase tracking-wide mb-3 border-b pb-2">
        Agent Analysis
      </h3>
      
      <div className="text-sm text-gray-700 leading-relaxed italic mb-4">
        "Based on unstructured community discussions, historical news sentiment, and local forums, the qualitative livability of this area is assessed at {(scores.livability_score || 0).toFixed(1)}/100."
      </div>
      
      <div className="flex justify-between items-center text-xs text-gray-500 bg-gray-50 p-2 rounded">
        <span>Confidence: {(scores.livability_confidence * 100).toFixed(0)}%</span>
        <span>Updated: {new Date(scores.last_updated).toLocaleDateString()}</span>
      </div>
    </div>
  );
}
