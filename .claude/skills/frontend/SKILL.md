---
name: frontend
description: Guidelines and instructions for the Frontend Layer.
---

# Frontend Layer Guidelines

When working on the Frontend Layer for TerraPulse, strictly adhere to the following rules:

1. **Tech Stack**: Map View Architecture must be powered by React, Vite, TailwindCSS, and `react-leaflet`.
2. **Map View Architecture**: `MapPage.tsx` manages the state for active overlays and the selected area detail side-panel.
3. **Choropleth Visualisation**: Use a generic `ScoreLayer.tsx` to dynamically color GeoJSON polygons fetched from PostGIS based on Price, Affordability, Safety, or Livability.
4. **Review Flag UI Rule (CRITICAL)**: To fulfill the contract from Phase 2/3, any area where `needs_human_review = True` MUST receive an unmissable visual warning marker. Display this both on the map directly (`AreaMarker.tsx`) and within the side panel (`ReviewFlagBanner.tsx`), explicitly stating that qualitative data disagrees with hard metrics.
