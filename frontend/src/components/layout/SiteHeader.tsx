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
    <header className="h-16 w-full bg-slate-950/95 backdrop-blur border-b border-slate-800 flex items-center px-6 sticky top-0 z-30">
      {/* Brand */}
      <button
        onClick={() => navigate("/")}
        className="flex items-center mr-8"
      >
        <span className="font-display text-xl font-semibold tracking-tight text-slate-50">
          Terra<span className="text-violet-400">Pulse</span>
        </span>
      </button>

      {/* Nav */}
      <nav className="flex items-center gap-1">
        {navItems.map((item) => (
          <button
            key={item.label}
            onClick={() => navigate(item.path)}
            className={`px-3 py-1.5 text-sm font-medium rounded-md transition-colors ${
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
      <div className="ml-auto">
        <button className="px-4 py-1.5 text-sm font-medium text-violet-400 border border-violet-500/40 rounded-lg hover:bg-violet-500/10 transition-colors">
          Sign in
        </button>
      </div>
    </header>
  );
}
