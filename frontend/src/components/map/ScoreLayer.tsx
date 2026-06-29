import React, { useEffect } from "react";
import { useMap } from "@vis.gl/react-google-maps";
import { AreaDetail, AreaScoreOutput } from "../../types/api";
import { ScoreType, getColorForScore } from "../../lib/colourScales";

interface ScoreLayerProps {
  areas: AreaDetail[];
  activeScoreType: ScoreType;
  scoresCache: Record<number, AreaScoreOutput>;
  onAreaClick: (areaId: number) => void;
}

export function ScoreLayer({ areas, activeScoreType, scoresCache, onAreaClick }: ScoreLayerProps) {
  const map = useMap();

  useEffect(() => {
    if (!map) return;
    
    // Clear existing data
    map.data.forEach((feature) => map.data.remove(feature));

    // Add areas as GeoJSON
    areas.forEach(area => {
      if (area.geometry) {
        try {
          const geoJsonFeature = {
            type: "Feature",
            geometry: area.geometry,
            properties: {
              areaId: area.id,
              name: area.name,
              avg_price: area.metrics?.avg_price
            }
          };
          map.data.addGeoJson(geoJsonFeature);
        } catch (e) {
          console.error("Failed to add GeoJSON for area", area.id, e);
        }
      }
    });
  }, [map, areas]);

  useEffect(() => {
    if (!map) return;
    
    // Style the layer based on the active score type
    map.data.setStyle((feature) => {
      const areaId = feature.getProperty("areaId");
      const avg_price = feature.getProperty("avg_price");
      const scoreData = scoresCache[areaId];
      
      let val = null;
      if (activeScoreType === "price") val = avg_price;
      else if (activeScoreType === "affordability" && scoreData) val = scoreData.affordability_score;
      else if (activeScoreType === "safety" && scoreData) val = scoreData.safety_score;
      else if (activeScoreType === "livability" && scoreData) val = scoreData.livability_score;

      return {
        fillColor: getColorForScore(activeScoreType, val),
        fillOpacity: 0.6,
        strokeColor: "#ffffff",
        strokeWeight: 1,
        zIndex: 1
      };
    });
  }, [map, activeScoreType, scoresCache]);

  useEffect(() => {
    if (!map) return;
    
    const clickListener = map.data.addListener("click", (e: any) => {
      const areaId = e.feature.getProperty("areaId");
      if (areaId) onAreaClick(areaId);
    });

    return () => {
      google.maps.event.removeListener(clickListener);
    };
  }, [map, onAreaClick]);

  return null;
}
