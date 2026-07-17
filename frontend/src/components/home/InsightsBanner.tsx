import React, { useMemo } from "react";
import { useNavigate } from "react-router-dom";
import { useAreaSummaries } from "../../hooks/useAreas";

// TODO: wire GET /v1/insights/summary once it exists. Until then this derives
// real, simple numbers from GET /v1/areas/summary (already fetched app-wide)
// rather than hardcoding fake percentages.
export function InsightsBanner() {
  const navigate = useNavigate();
  const { data: areas } = useAreaSummaries();

  const stats = useMemo(() => {
    if (!areas || areas.length === 0) return null;
    const sorted = [...areas].sort((a, b) => b.avg_price - a.avg_price);
    const top3 = sorted.slice(0, 3);
    const overallAvg = areas.reduce((sum, a) => sum + a.avg_price, 0) / areas.length;
    const totalSales = areas.reduce((sum, a) => sum + a.property_count, 0);
    const max = top3[0]?.avg_price || 1;
    return { top3, overallAvg, totalSales, max, trackedAreas: areas.length };
  }, [areas]);

  return (
    <section className="bg-gradient-to-r from-violet-950 to-slate-900 border-y border-violet-500/20">
      <div className="max-w-6xl mx-auto px-6 py-14 grid grid-cols-1 lg:grid-cols-2 gap-10 items-center">
        <div>
          <p className="font-mono text-xs font-semibold text-violet-400 uppercase tracking-widest mb-2">
            Market Insights
          </p>
          <h2 className="font-display text-2xl md:text-3xl font-semibold text-slate-50 mb-3">
            Dublin's property market at a glance
          </h2>
          <p className="text-slate-400 leading-relaxed mb-6">
            {stats
              ? `Tracking ${stats.trackedAreas} areas and ${stats.totalSales.toLocaleString()} recorded sales, the average price across TerraPulse-covered Dublin areas is €${Math.round(stats.overallAvg).toLocaleString("en-IE")}. ${stats.top3[0]?.name ?? ""} leads at €${stats.top3[0]?.avg_price.toLocaleString("en-IE") ?? ""} average.`
              : "Real-time price, safety, and livability trends across Dublin's postal districts and suburbs."}
          </p>
          <button
            onClick={() => navigate("/insights")}
            className="border border-violet-400 text-violet-400 hover:bg-violet-500 hover:text-white transition-colors px-5 py-2.5 rounded-lg text-sm font-medium"
          >
            Explore full analysis
          </button>
        </div>

        <div className="bg-slate-900/60 border border-slate-700 rounded-2xl p-6">
          {stats ? (
            <>
              <p className="text-xs text-slate-500 font-mono mb-4 uppercase tracking-wide">
                Highest average price by area
              </p>
              <svg viewBox="0 0 320 140" className="w-full h-auto" role="img" aria-label="Bar chart of the three highest average-price areas">
                {stats.top3.map((area, i) => {
                  const barHeight = Math.max(8, (area.avg_price / stats.max) * 80);
                  const x = i * 110 + 20;
                  return (
                    <g key={area.id}>
                      <rect
                        x={x}
                        y={110 - barHeight}
                        width={60}
                        height={barHeight}
                        rx={6}
                        fill="#a78bfa"
                        opacity={1 - i * 0.2}
                      />
                      <text x={x + 30} y={126} textAnchor="middle" fontSize="11" fill="#94a3b8" fontFamily="Inter, sans-serif">
                        {area.name}
                      </text>
                      <text
                        x={x + 30}
                        y={110 - barHeight - 6}
                        textAnchor="middle"
                        fontSize="11"
                        fill="#e2e8f0"
                        fontFamily="JetBrains Mono, monospace"
                        fontWeight={600}
                      >
                        €{Math.round(area.avg_price / 1000)}k
                      </text>
                    </g>
                  );
                })}
              </svg>
            </>
          ) : (
            <div className="h-32 flex items-center justify-center text-slate-500 text-sm">
              Loading market data...
            </div>
          )}
        </div>
      </div>
    </section>
  );
}
