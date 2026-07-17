import React from "react";
import { useNavigate } from "react-router-dom";
import { useAreaDetail } from "../../hooks/useAreas";
import { useAreaScore } from "../../hooks/useAreaScore";
import { ScoreSummaryCard } from "./ScoreSummaryCard";
import { AgentSummaryBlock } from "./AgentSummaryBlock";
import { ReviewFlagBanner } from "./ReviewFlagBanner";
import { PricePredictorWidget } from "../prediction/PricePredictorWidget";
import { LoadingState } from "../shared/LoadingState";
import { ErrorState } from "../shared/ErrorState";
import { X, ArrowRight } from "lucide-react";

export function AreaDetailPanel({ areaId, onClose }: { areaId: number | null; onClose: () => void }) {
  const navigate = useNavigate();
  const { data: area, isLoading: isAreaLoading, error: areaError, refetch: refetchArea } = useAreaDetail(areaId);
  const { data: scores, isLoading: isScoresLoading, error: scoresError, refetch: refetchScores } = useAreaScore(areaId);

  if (!areaId) return null;

  return (
    <div className="absolute top-0 right-0 h-full w-full sm:w-80 bg-slate-900 border-l border-slate-700 shadow-2xl flex flex-col z-[1000] overflow-y-auto animate-fade-up">
      <div className="p-4 bg-slate-900/95 backdrop-blur border-b border-slate-700 text-slate-50 flex justify-between items-center sticky top-0 z-10">
        <h2 className="font-display text-lg font-semibold truncate">{area?.name || "Loading Area..."}</h2>
        <button onClick={onClose} aria-label="Close area detail panel" className="p-1 hover:bg-slate-800 rounded flex-shrink-0">
          <X className="w-5 h-5" />
        </button>
      </div>

      <div className="flex-1 p-4">
        {(isAreaLoading || isScoresLoading) && <LoadingState message="Fetching area details..." />}

        {areaError && (
          <ErrorState message="Failed to load area data" onRetry={refetchArea} />
        )}

        {scoresError && (
          <ErrorState message="Failed to load area scores" onRetry={refetchScores} />
        )}

        {area && scores && (
          <>
            <ReviewFlagBanner needsReview={scores.needs_human_review} />

            <div className="mb-4 text-sm text-slate-400">
              <span className="font-medium text-slate-300 mr-2">{area.area_type}</span>
              <span className="text-slate-700">|</span>
              <span className="ml-2">Co. {area.county}</span>
            </div>

            {area.metrics && (
              <div className="grid grid-cols-2 gap-2 text-xs text-slate-400 mb-6 bg-slate-800/50 border border-slate-700 p-3 rounded-lg font-mono">
                <div>Population: <span className="font-medium text-slate-200">{area.metrics.population.toLocaleString()}</span></div>
                <div>Amenities: <span className="font-medium text-slate-200">{area.metrics.amenity_count.toLocaleString()}</span></div>
                <div>Crime Index: <span className="font-medium text-slate-200">{area.metrics.total_crime.toLocaleString()}</span></div>
                <div>Avg Sales: <span className="font-medium text-slate-200">€{area.metrics.avg_price.toLocaleString(undefined, { maximumFractionDigits: 0 })}</span></div>
              </div>
            )}

            <ScoreSummaryCard scores={scores} />
            <AgentSummaryBlock scores={scores} />
            <PricePredictorWidget area={area} />

            <button
              onClick={() => navigate(`/search?location=${encodeURIComponent(area.name)}`)}
              className="w-full mt-4 flex items-center justify-center gap-2 bg-violet-500 hover:bg-violet-600 text-white font-medium py-2.5 px-4 rounded-lg transition-colors"
            >
              View listings
              <ArrowRight className="w-4 h-4" aria-hidden="true" />
            </button>
          </>
        )}
      </div>
    </div>
  );
}
