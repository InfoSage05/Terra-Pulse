import React, { useMemo } from "react";
import { SiteHeader } from "../components/layout/SiteHeader";
import { useAreaSummaries } from "../hooks/useAreas";
import { useAreaScoresMap } from "../hooks/useAreaScoresMap";
import { ScorePill } from "../components/shared/ScorePill";
import { useNavigate } from "react-router-dom";
import { AlertTriangle, Loader2 } from "lucide-react";
import { areaPhotoUrl } from "../lib/images";

export function AreasPage() {
  const navigate = useNavigate();
  const { data: areas, isLoading, isError } = useAreaSummaries();
  const areaIds = useMemo(() => (areas ?? []).map((a) => a.id), [areas]);
  const scores = useAreaScoresMap(areaIds);

  return (
    <div className="min-h-screen bg-slate-950">
      <SiteHeader />

      <div className="max-w-6xl mx-auto px-6 py-10">
        <h1 className="font-display text-2xl font-semibold text-slate-50 mb-2">Dublin Areas</h1>
        <p className="text-sm text-slate-500 mb-8">
          {areas ? `${areas.length} areas` : "..."} tracked across postal districts and suburbs
        </p>

        {isLoading && (
          <div className="flex items-center justify-center py-16">
            <Loader2 className="w-6 h-6 text-violet-400 animate-spin" />
          </div>
        )}

        {isError && (
          <div className="text-center py-16 text-slate-500">
            Unable to load area data.
          </div>
        )}

        {areas && (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {areas.map((area, i) => {
              const areaScore = scores[area.id];
              return (
                <button
                  key={area.id}
                  onClick={() => navigate(`/search?location=${encodeURIComponent(area.name)}`)}
                  className="relative text-left bg-slate-900 border border-slate-700 rounded-2xl overflow-hidden hover:border-violet-500 transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-violet-500"
                >
                  <div className="relative h-[110px] overflow-hidden">
                    <img
                      src={areaPhotoUrl(area.id)}
                      alt=""
                      className="w-full h-full object-cover"
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

                  <div className="p-5">
                    <div className="flex items-start justify-between mb-2">
                      <h3 className="font-display font-bold text-slate-50">{area.name}</h3>
                      <span className="text-xs text-slate-400 bg-slate-800 px-2 py-0.5 rounded-full">
                        {area.area_type.replace("_", " ")}
                      </span>
                    </div>
                    <p className="text-xs text-slate-500 mb-4">{area.county}</p>

                    <div className="flex items-baseline gap-2 mb-4">
                      <span className="font-mono text-lg font-bold text-slate-50">
                        €{area.avg_price.toLocaleString("en-IE")}
                      </span>
                      <span className="text-xs text-slate-500">
                        avg · {area.property_count.toLocaleString()} sales
                      </span>
                    </div>

                    {areaScore && (
                      <div className="flex flex-wrap gap-1.5 mb-3">
                        {areaScore.safety_score != null && (
                          <ScorePill score={areaScore.safety_score} type="safety" size="sm" />
                        )}
                        {areaScore.livability_score != null && (
                          <ScorePill score={areaScore.livability_score} type="livability" size="sm" />
                        )}
                      </div>
                    )}

                    <div className="flex gap-4 text-xs border-t border-slate-800 pt-3">
                      <span className="text-slate-500">
                        Rank{" "}
                        <span className="font-bold text-violet-400 font-mono">
                          #{i + 1}
                        </span>
                      </span>
                    </div>
                  </div>
                </button>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
