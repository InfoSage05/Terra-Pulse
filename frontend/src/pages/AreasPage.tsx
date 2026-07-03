import React from "react";
import { SiteHeader } from "../components/layout/SiteHeader";
import { MOCK_AREAS, AREA_SCORES_MOCK } from "../data/mockData";
import { scoreColor } from "../lib/theme";
import { useNavigate } from "react-router-dom";

export function AreasPage() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-gray-50">
      <SiteHeader />

      <div className="max-w-6xl mx-auto px-6 py-10">
        <h1 className="text-2xl font-bold text-gray-900 mb-2">Dublin Areas</h1>
        <p className="text-sm text-gray-500 mb-8">
          {MOCK_AREAS.length} areas tracked across postal districts and suburbs
        </p>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {MOCK_AREAS.map((area) => {
            const scores = AREA_SCORES_MOCK[area.id];
            return (
              <button
                key={area.id}
                onClick={() => navigate(`/search?location=${encodeURIComponent(area.name)}`)}
                className="text-left bg-white rounded-xl p-5 border border-gray-200 hover:border-indigo-300 hover:shadow-md transition-all"
              >
                <div className="flex items-start justify-between mb-2">
                  <h3 className="font-semibold text-gray-900">{area.name}</h3>
                  <span className="text-xs text-gray-400 bg-gray-50 px-2 py-0.5 rounded-full">
                    {area.area_type.replace("_", " ")}
                  </span>
                </div>
                <p className="text-xs text-gray-400 mb-4">{area.county}</p>

                <div className="flex items-baseline gap-2 mb-4">
                  <span className="text-lg font-bold text-gray-900">
                    €{area.avg_price.toLocaleString()}
                  </span>
                  <span className="text-xs text-gray-500">avg · {area.property_count} listings</span>
                </div>

                {scores && (
                  <div className="flex gap-4 text-xs border-t border-gray-100 pt-3">
                    <span className="text-gray-500">
                      Safety <span className="font-bold" style={{ color: scoreColor(scores.safety) }}>{scores.safety ?? "—"}</span>
                    </span>
                    <span className="text-gray-500">
                      Afford <span className="font-bold" style={{ color: scoreColor(scores.affordability) }}>{scores.affordability ?? "—"}</span>
                    </span>
                    <span className="text-gray-500">
                      Live <span className="font-bold" style={{ color: scoreColor(scores.livability) }}>{scores.livability ?? "—"}</span>
                    </span>
                  </div>
                )}
              </button>
            );
          })}
        </div>
      </div>
    </div>
  );
}
