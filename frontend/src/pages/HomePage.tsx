import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Search, Sparkles, TrendingUp, Shield, Brain, Loader2 } from "lucide-react";
import { SiteHeader } from "../components/layout/SiteHeader";
import { useNeighborhoods } from "../hooks/useNeighborhoods";

export function HomePage() {
  const navigate = useNavigate();
  const [searchValue, setSearchValue] = useState("");
  const { data: hoods, isLoading } = useNeighborhoods({ limit: 8 });

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    navigate(`/search?location=${encodeURIComponent(searchValue)}`);
  };

  const handleNeighborhoodClick = (name: string) => {
    navigate(`/search?location=${encodeURIComponent(name)}`);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <SiteHeader />

      <section className="relative overflow-hidden bg-gradient-to-br from-indigo-600 via-indigo-700 to-purple-800">
        <div className="absolute inset-0 opacity-10" style={{
          backgroundImage: "radial-gradient(circle at 20% 50%, white 1px, transparent 1px), radial-gradient(circle at 80% 80%, white 1px, transparent 1px)",
          backgroundSize: "40px 40px",
        }} />
        <div className="relative max-w-3xl mx-auto px-6 py-24 text-center">
          <h1 className="text-4xl md:text-5xl font-extrabold tracking-tight text-white mb-4">
            Find your place in Dublin
          </h1>
          <p className="text-lg text-indigo-100 mb-10 max-w-xl mx-auto">
            Property prices, safety scores, and AI-verified livability signals — all in one map.
          </p>

          <form onSubmit={handleSearch} className="flex items-center gap-3 max-w-2xl mx-auto">
            <div className="flex-1 relative">
              <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="text"
                value={searchValue}
                onChange={(e) => setSearchValue(e.target.value)}
                placeholder="Enter a neighbourhood, e.g. Ranelagh, Ballsbridge..."
                className="w-full h-14 pl-12 pr-4 text-base bg-white rounded-2xl shadow-lg border-0 focus:outline-none focus:ring-4 focus:ring-indigo-300"
              />
            </div>
            <button
              type="submit"
              className="h-14 px-6 bg-gray-900 text-white font-semibold rounded-2xl shadow-lg hover:bg-gray-800 transition-colors whitespace-nowrap"
            >
              Search
            </button>
            <button
              type="button"
              onClick={() => navigate("/search")}
              className="h-14 w-14 flex items-center justify-center bg-white/20 text-white rounded-2xl shadow-lg hover:bg-white/30 transition-colors border border-white/30"
              title="Ask AI"
            >
              <Sparkles className="w-6 h-6" />
            </button>
          </form>
        </div>
      </section>

      <section className="max-w-6xl mx-auto px-6 py-16">
        <h2 className="text-2xl font-bold text-gray-900 mb-6">Featured Dublin neighbourhoods</h2>

        {isLoading && (
          <div className="flex items-center justify-center py-16">
            <Loader2 className="w-6 h-6 text-indigo-500 animate-spin" />
          </div>
        )}

        {hoods && (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {hoods.map((hood, i) => (
              <button
                key={hood.locality}
                onClick={() => handleNeighborhoodClick(hood.locality)}
                className="text-left bg-white rounded-xl p-5 border border-gray-200 hover:border-indigo-300 hover:shadow-md transition-all"
              >
                <div className="flex items-start justify-between mb-1">
                  <h3 className="font-semibold text-gray-900">{hood.locality}</h3>
                  {hood.eircode_district && (
                    <span className="text-xs text-gray-400 bg-gray-50 px-2 py-0.5 rounded-full">
                      {hood.eircode_district}
                    </span>
                  )}
                </div>
                {hood.median_sold_price && (
                  <p className="text-lg font-bold text-gray-900 mt-2">
                    €{Number(hood.median_sold_price).toLocaleString()}
                  </p>
                )}
                {hood.avg_asking_price && (
                  <p className="text-xs text-gray-400 mb-2">
                    asking: €{Number(hood.avg_asking_price).toLocaleString()}
                  </p>
                )}
                <div className="flex gap-3 text-xs border-t border-gray-100 pt-3 mt-1">
                  <span className="flex items-center gap-1 text-gray-500">
                    <span className="w-1.5 h-1.5 rounded-full bg-indigo-500 inline-block" />
                    Rank #{i + 1}
                  </span>
                  {hood.data_source && (
                    <span className="text-gray-400 truncate text-[10px] max-w-[200px]">
                      {hood.data_source.replace(/;.*$/, "")}
                    </span>
                  )}
                </div>
              </button>
            ))}
          </div>
        )}
      </section>

      <section className="bg-white border-t border-gray-100">
        <div className="max-w-6xl mx-auto px-6 py-16">
          <h2 className="text-2xl font-bold text-gray-900 mb-8">How TerraPulse works</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div>
              <div className="w-12 h-12 bg-indigo-50 rounded-xl flex items-center justify-center mb-4">
                <TrendingUp className="w-6 h-6 text-indigo-600" />
              </div>
              <h3 className="font-semibold text-gray-900 mb-2">Price prediction</h3>
              <p className="text-sm text-gray-500 leading-relaxed">
                ML-powered price estimates trained on real Property Price Register data, with confidence intervals.
              </p>
            </div>
            <div>
              <div className="w-12 h-12 bg-emerald-50 rounded-xl flex items-center justify-center mb-4">
                <Shield className="w-6 h-6 text-emerald-600" />
              </div>
              <h3 className="font-semibold text-gray-900 mb-2">Safety scores</h3>
              <p className="text-sm text-gray-500 leading-relaxed">
                Area-level safety ratings from recorded crime statistics, normalised per capita for fair comparison.
              </p>
            </div>
            <div>
              <div className="w-12 h-12 bg-violet-50 rounded-xl flex items-center justify-center mb-4">
                <Brain className="w-6 h-6 text-violet-600" />
              </div>
              <h3 className="font-semibold text-gray-900 mb-2">AI-verified livability</h3>
              <p className="text-sm text-gray-500 leading-relaxed">
                Agent-generated livability signals blending hard data with qualitative context, with human review flags.
              </p>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
