import React from "react";
import { SiteHeader } from "../components/layout/SiteHeader";

// Placeholder route — no dedicated /v1/insights endpoint exists yet (see the
// InsightsBanner on the homepage for the derived-from-real-data version of
// this and its `// TODO: wire GET /v1/insights/summary` stub).
export function InsightsPage() {
  return (
    <div className="min-h-screen bg-slate-950">
      <SiteHeader />
      <div className="flex items-center justify-center py-32">
        <div className="text-center">
          <h1 className="font-display text-2xl font-semibold text-slate-100 mb-2">Insights</h1>
          <p className="text-slate-500">Coming soon</p>
        </div>
      </div>
    </div>
  );
}
