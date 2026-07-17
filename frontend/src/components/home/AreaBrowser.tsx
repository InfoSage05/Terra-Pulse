import React, { useMemo } from "react";
import { useNavigate } from "react-router-dom";
import { AlertTriangle, ArrowRight, Loader2 } from "lucide-react";
import { useAreaSummaries } from "../../hooks/useAreas";
import { useAreaScoresMap } from "../../hooks/useAreaScoresMap";
import { ScorePill } from "../shared/ScorePill";
import { areaPhotoUrl } from "../../lib/images";

const HOME_PREVIEW_COUNT = 8;

export function AreaBrowser() {
  const navigate = useNavigate();
  const { data: areas, isLoading, isError } = useAreaSummaries();
  const previewAreas = useMemo(() => (areas ?? []).slice(0, HOME_PREVIEW_COUNT), [areas]);
  const areaIds = useMemo(() => previewAreas.map((a) => a.id), [previewAreas]);
  const scores = useAreaScoresMap(areaIds);

  // Affordability rank computed across the areas actually shown, using the
  // real affordability_score from GET /v1/areas/{id}/score.
  const affordabilityRank = useMemo(() => {
    const ranked = previewAreas
      .filter((a) => scores[a.id]?.affordability_score != null)
      .sort((a, b) => (scores[b.id].affordability_score ?? 0) - (scores[a.id].affordability_score ?? 0));
    const rankMap: Record<number, number> = {};
    ranked.forEach((a, i) => {
      rankMap[a.id] = i + 1;
    });
    return rankMap;
  }, [previewAreas, scores]);

  const goToArea = (name: string) => navigate(`/search?location=${encodeURIComponent(name)}`);

  return (
    <section className="max-w-6xl mx-auto px-6 py-12">
      <h2 className="font-display text-2xl md:text-3xl font-semibold text-slate-50 mb-6">
        Browse by area
      </h2>

      {isLoading && (
        <div className="flex items-center justify-center py-16">
          <Loader2 className="w-6 h-6 text-violet-400 animate-spin" />
        </div>
      )}

      {isError && (
        <div className="text-center py-16 text-slate-500">Unable to load area data. Please try again.</div>
      )}

      {!isLoading && !isError && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {previewAreas.map((area) => {
            const areaScore = scores[area.id];
            const rank = affordabilityRank[area.id];

            return (
              <div
                key={area.id}
                role="button"
                tabIndex={0}
                onClick={() => goToArea(area.name)}
                onKeyDown={(e) => {
                  if (e.key === "Enter" || e.key === " ") {
                    e.preventDefault();
                    goToArea(area.name);
                  }
                }}
                className="group relative bg-slate-900 border border-slate-700 rounded-2xl overflow-hidden cursor-pointer transition-colors hover:border-violet-500 focus:outline-none focus-visible:ring-2 focus-visible:ring-violet-500"
              >
                <div className="relative h-[120px] overflow-hidden">
                  <img
                    src={areaPhotoUrl(area.id)}
                    alt=""
                    className="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105"
                    loading="lazy"
                  />
                  {areaScore?.needs_human_review && (
                    <span
                      className="absolute top-2 right-2 flex items-center gap-1 bg-rose-500/90 text-white text-xs font-mono font-semibold px-2 py-0.5 rounded-md"
                      aria-label="Flagged for human review"
                    >
                      <AlertTriangle className="w-3 h-3" aria-hidden="true" />
                      Review
                    </span>
                  )}
                </div>

                <div className="p-4 pb-16">
                  <h3 className="font-display font-bold text-slate-50">{area.name}</h3>
                  <p className="font-mono text-lg text-slate-100 mt-1">
                    €{area.avg_price.toLocaleString("en-IE")}
                  </p>
                  <p className="text-xs text-slate-500 mb-3">
                    {area.property_count.toLocaleString()} listings
                  </p>
                  <div className="flex flex-wrap gap-1.5">
                    {areaScore?.safety_score != null && (
                      <ScorePill score={areaScore.safety_score} type="safety" size="sm" />
                    )}
                    {areaScore?.livability_score != null && (
                      <ScorePill score={areaScore.livability_score} type="livability" size="sm" />
                    )}
                  </div>
                </div>

                {/* Quick-stats drawer — slides up from the bottom on hover/focus. */}
                <div className="absolute bottom-0 left-0 right-0 bg-slate-800/95 backdrop-blur border-t border-slate-700 px-4 py-3 flex items-center justify-between translate-y-full group-hover:translate-y-0 group-focus-visible:translate-y-0 transition-transform duration-200">
                  <span className="text-xs text-slate-400 font-mono">
                    Affordability rank {rank ? `#${rank}` : "—"}
                  </span>
                  <span className="flex items-center gap-1 text-xs font-medium text-violet-400">
                    View area
                    <ArrowRight className="w-3 h-3" aria-hidden="true" />
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </section>
  );
}
