import React, { useState, useEffect } from "react";
import { APIProvider, Map } from "@vis.gl/react-google-maps";
import { useAreas } from "../../hooks/useAreas";
import { getAreaScore } from "../../api/areas";
import { AreaScoreOutput } from "../../types/api";
import { ScoreType } from "../../lib/colourScales";
import { ScoreLayer } from "../map/ScoreLayer";
import { LayerToggle } from "../map/LayerToggle";
import { AreaMarker } from "../map/AreaMarker";
import { AreaDetailPanel } from "../area-detail/AreaDetailPanel";
import { LoadingState } from "../shared/LoadingState";
import { ErrorState } from "../shared/ErrorState";

const API_KEY = import.meta.env.VITE_GOOGLE_MAPS_KEY || "dummy_key";
const DUBLIN_CENTER = { lat: 53.3498, lng: -6.2603 };

// Helper to compute a simple centroid from GeoJSON polygon
function getCentroid(geometry: any) {
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
  } catch (e) {
    return null;
  }
}

export function MapPage() {
  const { data: areas, isLoading, error, refetch } = useAreas();
  const [activeScoreType, setActiveScoreType] = useState<ScoreType>("price");
  const [selectedAreaId, setSelectedAreaId] = useState<number | null>(null);
  const [scoresCache, setScoresCache] = useState<Record<number, AreaScoreOutput>>({});

  // Background fetch of all scores for map flags and layers
  useEffect(() => {
    if (!areas) return;
    const fetchScores = async () => {
      const toFetch = areas.filter(a => !scoresCache[a.id]).slice(0, 50); // limit to avoid spam
      if (toFetch.length === 0) return;
      
      const newScores = { ...scoresCache };
      await Promise.all(
        toFetch.map(async (area) => {
          try {
            const score = await getAreaScore(area.id);
            newScores[area.id] = score;
          } catch (e) {
            console.error("Failed to fetch score", e);
          }
        })
      );
      setScoresCache(newScores);
    };
    
    fetchScores();
  }, [areas, scoresCache]);

  if (isLoading) return <div className="h-screen flex items-center justify-center"><LoadingState message="Loading map data..." /></div>;
  if (error) return <div className="h-screen flex items-center justify-center"><ErrorState message="Failed to load map data" onRetry={refetch} /></div>;

  return (
    <div className="h-screen w-full relative">
      <APIProvider apiKey={API_KEY}>
        <Map
          defaultCenter={DUBLIN_CENTER}
          defaultZoom={11}
          mapId="TERRAPULSE_MAP"
          disableDefaultUI={true}
        >
          <LayerToggle activeLayer={activeScoreType} onChange={setActiveScoreType} />
          
          <ScoreLayer 
            areas={areas || []} 
            activeScoreType={activeScoreType} 
            scoresCache={scoresCache}
            onAreaClick={setSelectedAreaId} 
          />
          
          {areas?.map((area) => {
            const score = scoresCache[area.id];
            if (score?.needs_human_review) {
              const centroid = getCentroid(area.geometry);
              if (centroid) {
                return (
                  <AreaMarker 
                    key={area.id}
                    lat={centroid.lat} 
                    lng={centroid.lng} 
                    needsReview={true} 
                    onClick={() => setSelectedAreaId(area.id)} 
                  />
                );
              }
            }
            return null;
          })}
        </Map>
      </APIProvider>
      
      {selectedAreaId && (
        <AreaDetailPanel 
          areaId={selectedAreaId} 
          onClose={() => setSelectedAreaId(null)} 
        />
      )}
    </div>
  );
}
