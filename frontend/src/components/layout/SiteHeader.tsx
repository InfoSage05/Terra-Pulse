import React from "react";
import { useNavigate, useLocation } from "react-router-dom";

export function SiteHeader() {
  const navigate = useNavigate();
  const location = useLocation();

  const isActive = (path: string) => location.pathname === path;

  const navItems = [
    { label: "For Sale", path: "/search" },
    { label: "Map", path: "/map" },
    { label: "Areas", path: "/areas" },
    { label: "Insights", path: "/insights" },
  ];

  return (
    <header className="h-16 w-full bg-slate-950/95 backdrop-blur border-b border-slate-800 flex items-center px-3 sm:px-6 gap-2 sticky top-0 z-30 overflow-x-auto scrollbar-hide">
      {/* Brand */}
      <button
        onClick={() => navigate("/")}
        className="flex items-center mr-2 sm:mr-8 flex-shrink-0"
      >
        <span className="font-display text-lg sm:text-xl font-semibold tracking-tight text-slate-50 whitespace-nowrap">
          Terra<span className="text-violet-400">Pulse</span>
        </span>
      </button>

      {/* Nav */}
      <nav className="flex items-center gap-1 flex-shrink-0">
        {navItems.map((item) => (
          <button
            key={item.label}
            onClick={() => navigate(item.path)}
            className={`px-2.5 sm:px-3 py-1.5 text-sm font-medium rounded-md transition-colors whitespace-nowrap ${
              isActive(item.path)
                ? "text-violet-400 bg-violet-500/10"
                : "text-slate-400 hover:text-slate-100 hover:bg-slate-800"
            }`}
          >
            {item.label}
          </button>
        ))}
      </nav>

      {/* Sign in */}
      <div className="ml-auto flex-shrink-0">
        <button className="px-3 sm:px-4 py-1.5 text-sm font-medium text-violet-400 border border-violet-500/40 rounded-lg hover:bg-violet-500/10 transition-colors whitespace-nowrap">
          Sign in
        </button>
      </div>
    </header>
  );
}
