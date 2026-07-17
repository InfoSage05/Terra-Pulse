import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Search, Sparkles } from "lucide-react";
import { HERO_IMAGE_URL } from "../../lib/images";

const TRUST_CHIPS = [
  "✦ 2,400+ listings",
  "⬡ AI-verified scores",
  "↻ Updated daily",
];

export function HeroSection() {
  const navigate = useNavigate();
  const [searchValue, setSearchValue] = useState("");

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    navigate(`/search?location=${encodeURIComponent(searchValue)}`);
  };

  return (
    <section className="relative overflow-hidden">
      <div className="absolute inset-0">
        <img
          src={HERO_IMAGE_URL}
          alt="Aerial view of Dublin, Ireland"
          className="w-full h-full object-cover"
        />
        <div className="absolute inset-0 bg-gradient-to-b from-violet-950/60 via-slate-950/80 to-slate-950" />
      </div>

      <div className="relative max-w-3xl mx-auto px-6 py-28 text-center">
        <h1
          className="animate-fade-up font-display font-bold text-white mb-4"
          style={{ animationDelay: "0ms", fontSize: "clamp(2.5rem, 6vw, 4.5rem)" }}
        >
          Find your place in Dublin
        </h1>
        <p
          className="animate-fade-up font-sans text-lg text-slate-400 mb-10 max-w-xl mx-auto"
          style={{ animationDelay: "100ms" }}
        >
          Property prices, safety scores, and AI-verified livability signals — all in one map.
        </p>

        <form
          onSubmit={handleSearch}
          className="animate-fade-up flex items-center gap-3 w-full max-w-2xl mx-auto"
          style={{ animationDelay: "200ms" }}
        >
          <div className="flex-1 relative">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-500" aria-hidden="true" />
            <input
              type="text"
              value={searchValue}
              onChange={(e) => setSearchValue(e.target.value)}
              placeholder="Enter an area, e.g. Dublin 8, Ranelagh..."
              aria-label="Search for an area"
              className="w-full h-14 pl-12 pr-4 text-base bg-slate-800 text-slate-100 placeholder:text-slate-500 rounded-full shadow-lg border border-slate-700 focus:outline-none focus:ring-4 focus:ring-violet-500/40 focus:border-violet-500"
            />
          </div>
          <button
            type="submit"
            className="h-14 px-6 bg-violet-500 text-white font-semibold rounded-full shadow-lg hover:bg-violet-600 transition-colors whitespace-nowrap"
          >
            Search
          </button>
          <button
            type="button"
            onClick={() => {
              const event = new CustomEvent("open-chat-widget");
              window.dispatchEvent(event);
            }}
            className="h-14 w-14 flex-shrink-0 flex items-center justify-center bg-white/10 text-white rounded-full shadow-lg hover:bg-white/20 transition-colors border border-white/20"
            aria-label="Ask AI assistant"
          >
            <Sparkles className="w-6 h-6" aria-hidden="true" />
          </button>
        </form>

        <div
          className="animate-fade-up flex flex-wrap items-center justify-center gap-2 mt-6"
          style={{ animationDelay: "300ms" }}
        >
          {TRUST_CHIPS.map((chip) => (
            <span
              key={chip}
              className="border border-slate-700 bg-slate-900/60 backdrop-blur text-slate-300 text-sm px-3 py-1 rounded-full"
            >
              {chip}
            </span>
          ))}
        </div>
      </div>
    </section>
  );
}
