// TerraPulse Design System
// Single source of truth for colors, typography, spacing, and score coding.
// Mirrors the CSS tokens defined in `index.css` (@theme block) — keep in sync.

export const colors = {
  brand: {
    DEFAULT: "#8b5cf6", // violet-500
    light: "#a78bfa",   // violet-400
    hover: "#7c3aed",   // violet-600
  },
  score: {
    high: "#34d399", // emerald-400 — score >= 75
    mid: "#fbbf24",  // amber-400   — score >= 50
    low: "#f43f5e",  // rose-500    — score < 50
  },
  surface: {
    950: "#020617", // page background
    900: "#0f172a", // card background
    800: "#1e293b", // elevated card / pill background
    700: "#334155", // border
    600: "#475569", // muted border / divider
  },
  text: {
    heading: "#f8fafc", // slate-50
    body: "#cbd5e1",    // slate-300
    muted: "#94a3b8",   // slate-400
    faint: "#64748b",   // slate-500
  },
} as const;

// Score colour coding — emerald (high) / amber (mid) / rose (low) / slate (null)
export function scoreColor(score: number | null | undefined): string {
  if (score === null || score === undefined) return "#64748b"; // slate-500 (no data)
  if (score >= 75) return colors.score.high;
  if (score >= 50) return colors.score.mid;
  return colors.score.low;
}

export const typeScale = {
  brand: "font-display text-xl font-semibold tracking-tight",
  heroTitle: "font-display font-bold tracking-tight text-white",
  heroSubtitle: "font-sans text-lg font-normal text-slate-400",
  cardPrice: "font-mono text-xl font-bold tracking-tight",
  cardBody: "font-sans text-sm font-normal",
  cardMeta: "font-sans text-xs font-normal",
  filterLabel: "font-sans text-xs font-medium",
  resultsCount: "font-sans text-sm font-medium",
  nav: "font-sans text-sm font-medium",
} as const;

export const radius = {
  sm: "rounded-md",
  DEFAULT: "rounded-lg",
  full: "rounded-full",
} as const;

export const spacing = {
  cardPadding: "px-5 py-4",
  filterGap: "gap-3",
  headerHeight: "h-16",
} as const;
