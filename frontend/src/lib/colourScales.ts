export type ScoreType = "price" | "affordability" | "safety" | "livability";

// Manual 3-stop colour interpolation (rose -> amber -> emerald), matching the
// ScorePill semantics (score.low / score.mid / score.high tokens in index.css).
// No chroma-js dependency — react-leaflet's GeoJSON `style` just needs a hex string.
const ROSE: [number, number, number] = [244, 63, 94]; // #f43f5e
const AMBER: [number, number, number] = [251, 191, 36]; // #fbbf24
const EMERALD: [number, number, number] = [52, 211, 153]; // #34d399
const NO_DATA = "#334155"; // slate-700

function lerp(a: number, b: number, t: number): number {
  return Math.round(a + (b - a) * t);
}

function mixRgb(c1: [number, number, number], c2: [number, number, number], t: number): [number, number, number] {
  return [lerp(c1[0], c2[0], t), lerp(c1[1], c2[1], t), lerp(c1[2], c2[2], t)];
}

function toHex([r, g, b]: [number, number, number]): string {
  const h = (n: number) => n.toString(16).padStart(2, "0");
  return `#${h(r)}${h(g)}${h(b)}`;
}

/** 0-100 -> rose (low) through amber (mid) to emerald (high). */
function scaleLowToHigh(pct: number): string {
  const clamped = Math.max(0, Math.min(100, pct));
  if (clamped <= 50) return toHex(mixRgb(ROSE, AMBER, clamped / 50));
  return toHex(mixRgb(AMBER, EMERALD, (clamped - 50) / 50));
}

/** Same ramp inverted — used for price, where a low price is "good" (emerald)
 * and a high price is "expensive" (rose). */
function scaleHighToLow(pct: number): string {
  return scaleLowToHigh(100 - pct);
}

export function getColorForScore(scoreType: ScoreType, score: number | null | undefined): string {
  if (score === null || score === undefined || isNaN(score)) return NO_DATA;

  if (scoreType === "price") {
    // Dublin sale prices roughly span 200k-1M; normalise into a 0-100 band.
    const pct = Math.max(0, Math.min(100, ((score - 200_000) / 800_000) * 100));
    return scaleHighToLow(pct);
  }

  // affordability / safety / livability are already 0-100 scores.
  return scaleLowToHigh(score);
}
