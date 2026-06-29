import React from "react";
import { useAreaDetail } from "../../hooks/useAreas";
import { useAreaScore } from "../../hooks/useAreaScore";
import { ScoreSummaryCard } from "./ScoreSummaryCard";
import { AgentSummaryBlock } from "./AgentSummaryBlock";
import { ReviewFlagBanner } from "./ReviewFlagBanner";
import { PricePredictorWidget } from "../prediction/PricePredictorWidget";
import { LoadingState } from "../shared/LoadingState";
import { ErrorState } from "../shared/ErrorState";
import { X } from "lucide-react";

export function AreaDetailPanel({ areaId, onClose }: { areaId: number | null; onClose: () => void }) {
  const { data: area, isLoading: isAreaLoading, error: areaError, refetch: refetchArea } = useAreaDetail(areaId);
  const { data: scores, isLoading: isScoresLoading, error: scoresError, refetch: refetchScores } = useAreaScore(areaId);

  if (!areaId) return null;

  return (
    <div className="absolute top-0 right-0 h-full w-96 bg-white shadow-xl flex flex-col z-10 overflow-y-auto">
      <div className="p-4 bg-indigo-700 text-white flex justify-between items-center sticky top-0 z-20 shadow-md">
        <h2 className="text-lg font-semibold">{area?.name || "Loading Area..."}</h2>
        <button onClick={onClose} className="p-1 hover:bg-indigo-600 rounded">
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
            
            <div className="mb-4 text-sm text-gray-600">
              <span className="font-medium mr-2">{area.area_type}</span>
              <span className="text-gray-400">|</span>
              <span className="ml-2">Co. {area.county}</span>
            </div>

            {area.metrics && (
              <div className="grid grid-cols-2 gap-2 text-xs text-gray-500 mb-6 bg-gray-50 p-3 rounded">
                <div>Population: <span className="font-medium text-gray-800">{area.metrics.population.toLocaleString()}</span></div>
                <div>Amenities: <span className="font-medium text-gray-800">{area.metrics.amenity_count.toLocaleString()}</span></div>
                <div>Crime Index: <span className="font-medium text-gray-800">{area.metrics.total_crime.toLocaleString()}</span></div>
                <div>Avg Sales: <span className="font-medium text-gray-800">€{area.metrics.avg_price.toLocaleString(undefined, { maximumFractionDigits: 0 })}</span></div>
              </div>
            )}

            <ScoreSummaryCard scores={scores} />
            <AgentSummaryBlock scores={scores} />
            <PricePredictorWidget area={area} />
          </>
        )}
      </div>
    </div>
  );
}
