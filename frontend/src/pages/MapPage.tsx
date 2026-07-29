import React, { useState, useEffect, useRef } from "react";
import { MapContainer, TileLayer, ZoomControl } from "react-leaflet";
import { useAreas } from "../hooks/useAreas";
import { getAreaScore, getAreaDetail } from "../api/areas";
import { AreaScoreOutput, AreaMetrics } from "../types/api";
import { ScoreType } from "../lib/colourScales";
import { ScoreLayer } from "../components/map/ScoreLayer";
import { LayerToggle } from "../components/map/LayerToggle";
import { AreaMarker } from "../components/map/AreaMarker";
import { AreaDetailPanel } from "../components/area-detail/AreaDetailPanel";
import { SiteHeader } from "../components/layout/SiteHeader";
import { getCentroid as getCentroidTuple } from "../lib/geo";

const DUBLIN_CENTER: [number, number] = [53.3498, -6.2603];
const DARK_TILE_URL = "https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png";

function getCentroid(geometry: any): { lat: number; lng: number } | null {
  const c = getCentroidTuple(geometry);
  return c ? { lat: c[0], lng: c[1] } : null;
}

export function MapPage() {
  const { data: areas, isLoading, error, refetch } = useAreas();
  const [activeScoreType, setActiveScoreType] = useState<ScoreType>("price");
  const [selectedAreaId, setSelectedAreaId] = useState<number | null>(null);
  const [scoresCache, setScoresCache] = useState<Record<number, AreaScoreOutput>>({});
  const scoresCacheRef = useRef(scoresCache);
  // GET /v1/areas/ (list) never includes `metrics` (only GET /v1/areas/{id} does),
  // so the "price" choropleth layer needs its own per-area fetch, mirroring the
  // scores fetch below, otherwise every polygon renders as "no data" gray.
  const [metricsCache, setMetricsCache] = useState<Record<number, AreaMetrics>>({});
  const metricsCacheRef = useRef(metricsCache);

  useEffect(() => {
    scoresCacheRef.current = scoresCache;
  }, [scoresCache]);

  useEffect(() => {
    metricsCacheRef.current = metricsCache;
  }, [metricsCache]);

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

    const fetchMetrics = async () => {
      const cache = metricsCacheRef.current;
      const toFetch = areas.filter(a => !cache[a.id]).slice(0, 50);
      if (toFetch.length === 0) return;

      const newMetrics = { ...cache };
      await Promise.all(
        toFetch.map(async (area: any) => {
          try {
            const detail = await getAreaDetail(area.id);
            if (detail.metrics) newMetrics[area.id] = detail.metrics;
          } catch {
            // metrics unavailable if backend is down
          }
        })
      );
      setMetricsCache(newMetrics);
    };

    fetchScores();
    fetchMetrics();
  }, [areas]);

  const reviewCount = Object.values(scoresCache).filter((s) => s.needs_human_review).length;

  return (
    <div className="h-screen w-full flex flex-col bg-slate-950">
      <SiteHeader />
      <div className="flex-1 relative">
        {isLoading && (
          <div className="absolute top-4 left-1/2 -translate-x-1/2 z-[1000] bg-slate-900/90 backdrop-blur border border-slate-700 rounded-full px-4 py-1.5 shadow-md text-sm text-slate-300 flex items-center gap-2">
            <div className="animate-spin rounded-full h-3 w-3 border border-violet-400 border-t-transparent" />
            Loading area data...
          </div>
        )}
        {error && (
          <div className="absolute top-4 left-1/2 -translate-x-1/2 z-[1000] bg-amber-400/10 border border-amber-400/30 rounded-lg px-4 py-2 shadow-md text-sm text-amber-300 flex items-center gap-2">
            Backend unavailable — showing map only
            <button onClick={() => refetch()} className="underline text-amber-200 ml-1">Retry</button>
          </div>
        )}
        {!isLoading && !error && reviewCount > 0 && (
          <div className="absolute bottom-4 left-4 z-[1000] bg-rose-500/10 border border-rose-500/40 rounded-lg px-3 py-2 shadow-md text-xs text-rose-300 flex items-center gap-2 max-w-xs">
            {reviewCount} area{reviewCount === 1 ? "" : "s"} flagged for human review — pulsing markers on the map.
          </div>
        )}

        <LayerToggle activeLayer={activeScoreType} onChange={setActiveScoreType} />

        <MapContainer
          center={DUBLIN_CENTER}
          zoom={11}
          scrollWheelZoom
          zoomControl={false}
          style={{ height: "100%", width: "100%", background: "#020617" }}
        >
          <ZoomControl position="bottomright" />
          <TileLayer
            url={DARK_TILE_URL}
            attribution='&copy; <a href="https://carto.com/attributions">CARTO</a> &copy; OpenStreetMap contributors'
          />

          <ScoreLayer
            areas={areas || []}
            activeScoreType={activeScoreType}
            scoresCache={scoresCache}
            metricsCache={metricsCache}
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
        </MapContainer>

        {selectedAreaId && (
          <AreaDetailPanel
            areaId={selectedAreaId}
            onClose={() => setSelectedAreaId(null)}
          />
        )}
      </div>
    </div>
  );
}
