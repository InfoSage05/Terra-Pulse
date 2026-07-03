// TerraPulse Design System
// Single source of truth for colors, typography, spacing, and score coding

export const colors = {
  brand: {
    DEFAULT: "#4f46e5", // indigo-600 — distinct from Zillow's pure blue
    hover: "#4338ca",   // indigo-700
    light: "#eef2ff",   // indigo-50
    accent: "#0ea5e9",  // sky-500 — wordmark accent
  },
  success: "#16a34a",   // green-600
  warning: {
    DEFAULT: "#d97706", // amber-600
    light: "#fffbeb",   // amber-50
    border: "#fcd34d",  // amber-300
  },
  danger: "#dc2626",    // red-600
  text: {
    heading: "#111827", // gray-900
    body: "#374151",    // gray-700
    muted: "#6b7280",   // gray-500
    faint: "#9ca3af",   // gray-400
  },
  surface: {
    DEFAULT: "#ffffff",
    subtle: "#f9fafb",  // gray-50 — page background
    card: "#ffffff",    // white cards on grey page
    border: "#e5e7eb",  // gray-200
  },
} as const;

// Score colour coding — green (high), amber (mid), red (low), grey (null)
export function scoreColor(score: number | null | undefined): string {
  if (score === null || score === undefined) return "#9ca3af"; // gray-400
  if (score >= 70) return "#16a34a"; // green-600
  if (score >= 40) return "#d97706"; // amber-600
  return "#dc2626"; // red-600
}

export const typeScale = {
  brand: "text-xl font-bold tracking-tight",
  heroTitle: "text-4xl font-extrabold tracking-tight",
  heroSubtitle: "text-lg font-normal",
  cardPrice: "text-xl font-extrabold tracking-tight",
  cardBody: "text-sm font-normal",
  cardMeta: "text-xs font-normal",
  filterLabel: "text-xs font-medium",
  resultsCount: "text-sm font-medium",
  nav: "text-sm font-medium",
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
