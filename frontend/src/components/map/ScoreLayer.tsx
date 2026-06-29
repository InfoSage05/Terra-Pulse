import React from "react";
import { GeoJSON } from "react-leaflet";
import { AreaDetail, AreaScoreOutput } from "../../types/api";
import { ScoreType, getColorForScore } from "../../lib/colourScales";
import { Layer } from "leaflet";

interface ScoreLayerProps {
  areas: AreaDetail[];
  activeScoreType: ScoreType;
  scoresCache: Record<number, AreaScoreOutput>;
  onAreaClick: (areaId: number) => void;
}

export function ScoreLayer({ areas, activeScoreType, scoresCache, onAreaClick }: ScoreLayerProps) {
  
  const getFeatureStyle = (feature: any) => {
    const areaId = feature.properties.areaId;
    const avg_price = feature.properties.avg_price;
    const scoreData = scoresCache[areaId];
    
    let val = null;
    if (activeScoreType === "price") val = avg_price;
    else if (activeScoreType === "affordability" && scoreData) val = scoreData.affordability_score;
    else if (activeScoreType === "safety" && scoreData) val = scoreData.safety_score;
    else if (activeScoreType === "livability" && scoreData) val = scoreData.livability_score;

    return {
      fillColor: getColorForScore(activeScoreType, val),
      weight: 1,
      opacity: 1,
      color: 'white',
      fillOpacity: 0.6
    };
  };

  const onEachFeature = (feature: any, layer: Layer) => {
    const areaId = feature.properties.areaId;
    layer.on({
      click: () => {
        if (areaId) onAreaClick(areaId);
      }
    });
  };

  return (
    <>
      {areas.map(area => {
        if (!area.geometry) return null;
        
        const geoJsonFeature = {
          type: "Feature" as const,
          geometry: area.geometry,
          properties: {
            areaId: area.id,
            name: area.name,
            avg_price: area.metrics?.avg_price
          }
        };

        // We use a unique key combining area id and active score type so React completely re-renders the GeoJSON component when styles change
        return (
          <GeoJSON 
            key={`${area.id}-${activeScoreType}`} 
            data={geoJsonFeature} 
            style={getFeatureStyle}
            onEachFeature={onEachFeature}
          />
        );
      })}
    </>
  );
}
