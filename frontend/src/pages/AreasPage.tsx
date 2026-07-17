import React from "react";
import { SiteHeader } from "../components/layout/SiteHeader";
import { useAreaSummaries } from "../hooks/useAreas";
import { useNavigate } from "react-router-dom";
import { Loader2 } from "lucide-react";

export function AreasPage() {
  const navigate = useNavigate();
  const { data: areas, isLoading, isError } = useAreaSummaries();

  return (
    <div className="min-h-screen bg-gray-50">
      <SiteHeader />

      <div className="max-w-6xl mx-auto px-6 py-10">
        <h1 className="text-2xl font-bold text-gray-900 mb-2">Dublin Areas</h1>
        <p className="text-sm text-gray-500 mb-8">
          {areas ? `${areas.length} areas` : "..."} tracked across postal districts and suburbs
        </p>

        {isLoading && (
          <div className="flex items-center justify-center py-16">
            <Loader2 className="w-6 h-6 text-indigo-500 animate-spin" />
          </div>
        )}

        {isError && (
          <div className="text-center py-16 text-gray-400">
            Unable to load area data.
          </div>
        )}

        {areas && (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {areas.map((area) => (
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
                  <span className="text-xs text-gray-500">
                    avg · {area.property_count.toLocaleString()} sales
                  </span>
                </div>

                <div className="flex gap-4 text-xs border-t border-gray-100 pt-3">
                  <span className="text-gray-500">
                    Rank{" "}
                    <span className="font-bold text-indigo-600">
                      #{areas.indexOf(area) + 1}
                    </span>
                  </span>
                </div>
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
