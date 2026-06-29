export type ScoreType = "price" | "affordability" | "safety" | "livability";

const GOOD_COLORS = ["#ef4444", "#f97316", "#facc15", "#84cc16", "#22c55e"]; // red to green
const PRICE_COLORS = ["#22c55e", "#84cc16", "#facc15", "#f97316", "#ef4444"]; // green to red (low price is green)

export function getColorForScore(scoreType: ScoreType, score: number | null | undefined): string {
  if (score === null || score === undefined || isNaN(score)) return "#e5e7eb"; // gray-200 for no data
  
  let colors = GOOD_COLORS;
  let normalizedScore = score; // 0-100 expected
  
  if (scoreType === "price") {
    colors = PRICE_COLORS;
    // Assume price ranges from 200k to 1m for Dublin mapping roughly
    normalizedScore = Math.max(0, Math.min(100, ((score - 200000) / 800000) * 100));
  }
  
  // bucket into 5 colors (0-19, 20-39, 40-59, 60-79, 80-100)
  const index = Math.min(4, Math.floor(normalizedScore / 20));
  return colors[index] || "#e5e7eb";
}
