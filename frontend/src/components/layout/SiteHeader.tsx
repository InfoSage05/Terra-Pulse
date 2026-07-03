import React from "react";
import { useNavigate, useLocation } from "react-router-dom";

export function SiteHeader() {
  const navigate = useNavigate();
  const location = useLocation();

  const isActive = (path: string) => location.pathname === path;

  const navItems = [
    { label: "For Sale", path: "/search" },
    { label: "Areas", path: "/areas" },
    { label: "Insights", path: "/insights" },
  ];

  return (
    <header className="h-16 w-full bg-white border-b border-gray-200 flex items-center px-6 sticky top-0 z-30 shadow-sm">
      {/* Brand */}
      <button
        onClick={() => navigate("/")}
        className="flex items-center mr-8"
      >
        <span className="text-xl font-bold tracking-tight text-gray-900">
          Terra<span className="text-sky-500">Pulse</span>
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
                ? "text-indigo-600 bg-indigo-50"
                : "text-gray-600 hover:text-gray-900 hover:bg-gray-50"
            }`}
          >
            {item.label}
          </button>
        ))}
      </nav>

      {/* Sign in */}
      <div className="ml-auto">
        <button className="px-4 py-1.5 text-sm font-medium text-indigo-600 border border-indigo-200 rounded-lg hover:bg-indigo-50 transition-colors">
          Sign in
        </button>
      </div>
    </header>
  );
}
