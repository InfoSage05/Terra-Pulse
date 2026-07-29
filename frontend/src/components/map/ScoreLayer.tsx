import React from "react";
import { GeoJSON } from "react-leaflet";
import type { Feature, Geometry } from "geojson";
import { AreaDetail, AreaMetrics, AreaScoreOutput } from "../../types/api";
import { ScoreType, getColorForScore } from "../../lib/colourScales";

interface ScoreLayerProps {
  areas: AreaDetail[];
  activeScoreType: ScoreType;
  scoresCache: Record<number, AreaScoreOutput>;
  metricsCache?: Record<number, AreaMetrics>;
  onAreaClick: (areaId: number) => void;
}

function getScoreValue(
  area: AreaDetail,
  scoreData: AreaScoreOutput | undefined,
  metricsData: AreaMetrics | undefined,
  scoreType: ScoreType
): number | null | undefined {
  // GET /v1/areas/ (list) never includes `metrics`, so area.metrics is always
  // undefined here — fall back to the per-area metrics fetched separately
  // (MapPage's metricsCache, sourced from GET /v1/areas/{id}).
  if (scoreType === "price") return area.metrics?.avg_price ?? metricsData?.avg_price;
  if (!scoreData) return null;
  if (scoreType === "affordability") return scoreData.affordability_score;
  if (scoreType === "safety") return scoreData.safety_score;
  if (scoreType === "livability") return scoreData.livability_score;
  return null;
}

/**
 * Choropleth layer: one Leaflet <GeoJSON> polygon per area, colour-scaled to
 * the active overlay (price / affordability / safety / livability). Areas'
 * `geometry` is already GeoJSON (lng/lat order) straight from PostGIS via the
 * backend — no coordinate conversion needed (unlike the old Google Maps
 * Polygon implementation, which had to flip to {lat,lng} pairs by hand).
 */
export function ScoreLayer({ areas, activeScoreType, scoresCache, metricsCache, onAreaClick }: ScoreLayerProps) {
  return (
    <>
      {areas.map((area) => {
        if (!area.geometry) return null;

        const scoreData = scoresCache[area.id];
        const metricsData = metricsCache?.[area.id];
        const val = getScoreValue(area, scoreData, metricsData, activeScoreType);
        const fillColor = getColorForScore(activeScoreType, val);

        const feature: Feature<Geometry> = {
          type: "Feature",
          properties: { id: area.id },
          geometry: area.geometry,
        };

        return (
          <GeoJSON
            key={`${area.id}-${activeScoreType}-${fillColor}`}
            data={feature}
            style={{
              fillColor,
              fillOpacity: 0.55,
              color: "#ffffff",
              weight: 1,
            }}
            eventHandlers={{
              click: () => onAreaClick(area.id),
              mouseover: (e) => e.target.setStyle({ fillOpacity: 0.75, weight: 2 }),
              mouseout: (e) => e.target.setStyle({ fillOpacity: 0.55, weight: 1 }),
            }}
          />
        );
      })}
    </>
  );
}
