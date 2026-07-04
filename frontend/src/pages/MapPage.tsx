import React, { useState, useEffect, useRef } from "react";
import { Map } from "@vis.gl/react-google-maps";
import { useAreas } from "../hooks/useAreas";
import { getAreaScore } from "../api/areas";
import { AreaScoreOutput } from "../types/api";
import { ScoreType } from "../lib/colourScales";
import { ScoreLayer } from "../components/map/ScoreLayer";
import { LayerToggle } from "../components/map/LayerToggle";
import { AreaMarker } from "../components/map/AreaMarker";
import { AreaDetailPanel } from "../components/area-detail/AreaDetailPanel";

const DUBLIN_CENTER = { lat: 53.3498, lng: -6.2603 };

function getCentroid(geometry: any): { lat: number; lng: number } | null {
  if (!geometry || !geometry.coordinates) return null;

  try {
    let coords = geometry.coordinates;
    if (geometry.type === "MultiPolygon") {
      coords = coords[0][0];
    } else if (geometry.type === "Polygon") {
      coords = coords[0];
    }

    if (!coords || coords.length === 0 || !Array.isArray(coords[0])) return null;

    let sumLat = 0, sumLng = 0;
    coords.forEach(([lng, lat]: [number, number]) => {
      sumLat += lat;
      sumLng += lng;
    });
    return { lat: sumLat / coords.length, lng: sumLng / coords.length };
  } catch {
    return null;
  }
}

export function MapPage() {
  const { data: areas, isLoading, error, refetch } = useAreas();
  const [activeScoreType, setActiveScoreType] = useState<ScoreType>("price");
  const [selectedAreaId, setSelectedAreaId] = useState<number | null>(null);
  const [scoresCache, setScoresCache] = useState<Record<number, AreaScoreOutput>>({});
  const scoresCacheRef = useRef(scoresCache);

  useEffect(() => {
    scoresCacheRef.current = scoresCache;
  }, [scoresCache]);

  useEffect(() => {
    if (!areas) return;
    const fetchScores = async () => {
      const cache = scoresCacheRef.current;
      const toFetch = areas.filter(a => !cache[a.id]).slice(0, 50);
      if (toFetch.length === 0) return;

      const newScores = { ...cache };
      await Promise.all(
        toFetch.map(async (area: any) => {
          try {
            const score = await getAreaScore(area.id);
            newScores[area.id] = score;
          } catch {
            // scores unavailable if backend is down
          }
        })
      );
      setScoresCache(newScores);
    };

    fetchScores();
  }, [areas]);

  return (
    <div className="h-screen w-full relative">
      {isLoading && (
        <div className="absolute top-14 left-1/2 -translate-x-1/2 z-20 bg-white/90 backdrop-blur rounded-full px-4 py-1.5 shadow-md text-sm text-gray-500 flex items-center gap-2">
          <div className="animate-spin rounded-full h-3 w-3 border border-indigo-600 border-t-transparent" />
          Loading area data...
        </div>
      )}
      {error && (
        <div className="absolute top-14 left-1/2 -translate-x-1/2 z-20 bg-amber-50 border border-amber-200 rounded-lg px-4 py-2 shadow-md text-sm text-amber-800 flex items-center gap-2">
          Backend unavailable — showing map only
          <button onClick={() => refetch()} className="underline text-amber-900 ml-1">Retry</button>
        </div>
      )}
      <LayerToggle activeLayer={activeScoreType} onChange={setActiveScoreType} />

      <Map
        defaultCenter={DUBLIN_CENTER}
        defaultZoom={11}
        style={{ height: "100%", width: "100%" }}
        gestureHandling="greedy"
        disableDefaultUI={false}
        zoomControl={false}
      >
        <ScoreLayer
          areas={areas || []}
          activeScoreType={activeScoreType}
          scoresCache={scoresCache}
          onAreaClick={setSelectedAreaId}
        />

        {areas?.map((area: any) => {
          const score = scoresCache[area.id];
          if (score?.needs_human_review) {
            const centroid = getCentroid(area.geometry);
            if (centroid) {
              return (
                <AreaMarker
                  key={area.id}
                  position={centroid}
                  needsReview={true}
                  onClick={() => setSelectedAreaId(area.id)}
                />
              );
            }
          }
          return null;
        })}
      </Map>

      {selectedAreaId && (
        <AreaDetailPanel
          areaId={selectedAreaId}
          onClose={() => setSelectedAreaId(null)}
        />
      )}
    </div>
  );
}
