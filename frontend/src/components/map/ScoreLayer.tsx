import React from "react";
import { Polygon } from "@vis.gl/react-google-maps";
import { AreaDetail, AreaScoreOutput } from "../../types/api";
import { ScoreType, getColorForScore } from "../../lib/colourScales";

interface ScoreLayerProps {
  areas: AreaDetail[];
  activeScoreType: ScoreType;
  scoresCache: Record<number, AreaScoreOutput>;
  onAreaClick: (areaId: number) => void;
}

function geoJsonCoordsToPaths(geometry: any): google.maps.LatLngLiteral[][] {
  if (!geometry || !geometry.coordinates) return [];

  const convertRing = (ring: number[][]): google.maps.LatLngLiteral[] =>
    ring.map(([lng, lat]) => ({ lat, lng }));

  if (geometry.type === "Polygon") {
    return geometry.coordinates.map(convertRing);
  }
  if (geometry.type === "MultiPolygon") {
    return geometry.coordinates.flatMap((polygon: number[][][]) =>
      polygon.map(convertRing)
    );
  }
  return [];
}

function getScoreValue(area: AreaDetail, scoreData: AreaScoreOutput | undefined, scoreType: ScoreType): number | null | undefined {
  if (scoreType === "price") return area.metrics?.avg_price;
  if (!scoreData) return null;
  if (scoreType === "affordability") return scoreData.affordability_score;
  if (scoreType === "safety") return scoreData.safety_score;
  if (scoreType === "livability") return scoreData.livability_score;
  return null;
}

export function ScoreLayer({ areas, activeScoreType, scoresCache, onAreaClick }: ScoreLayerProps) {
  return (
    <>
      {areas.map(area => {
        if (!area.geometry) return null;
        const paths = geoJsonCoordsToPaths(area.geometry);
        if (paths.length === 0) return null;

        const scoreData = scoresCache[area.id];
        const val = getScoreValue(area, scoreData, activeScoreType);
        const fillColor = getColorForScore(activeScoreType, val);

        return (
          <Polygon
            key={`${area.id}-${activeScoreType}`}
            paths={paths}
            options={{
              fillColor,
              fillOpacity: 0.55,
              strokeColor: "#ffffff",
              strokeWeight: 1,
            }}
            onClick={() => onAreaClick(area.id)}
          />
        );
      })}
    </>
  );
}
