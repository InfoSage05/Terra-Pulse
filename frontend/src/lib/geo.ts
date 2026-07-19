// Shared by MapPage, MapPreviewStrip, and SearchPage - all three need to turn
// an area's GeoJSON polygon into a single point to drop a marker on.
export function getCentroid(geometry: any): [number, number] | null {
  if (!geometry || !geometry.coordinates) return null;
  try {
    let coords = geometry.coordinates;
    if (geometry.type === "MultiPolygon") coords = coords[0][0];
    else if (geometry.type === "Polygon") coords = coords[0];
    if (!coords || coords.length === 0 || !Array.isArray(coords[0])) return null;

    let sumLat = 0, sumLng = 0;
    coords.forEach(([lng, lat]: [number, number]) => {
      sumLat += lat;
      sumLng += lng;
    });
    return [sumLat / coords.length, sumLng / coords.length];
  } catch {
    return null;
  }
}

// Small deterministic offset (~0-250m) so multiple properties that share an
// area centroid (no per-property geocoding exists in this dataset - see
// PropertyMarker's `approximate` prop) don't render as a single stacked dot.
// Deterministic on `seed` (the property id) so a given property always
// lands in the same spot rather than jumping around on re-render.
export function jitterCentroid(center: [number, number], seed: number): [number, number] {
  const angle = (seed * 137.508) % 360; // golden-angle spread, avoids clustering
  const radiusDeg = 0.0015 + ((seed * 9301 + 49297) % 233) / 233 * 0.001; // ~150-260m
  const rad = (angle * Math.PI) / 180;
  return [center[0] + Math.sin(rad) * radiusDeg, center[1] + Math.cos(rad) * radiusDeg];
}
