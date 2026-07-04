import React, { useState, useEffect } from "react";
import { Map, useMap } from "@vis.gl/react-google-maps";
import { useSearchParams } from "react-router-dom";
import { SiteHeader } from "../components/layout/SiteHeader";
import { SplitLayout } from "../components/layout/SplitLayout";
import { SearchHeader } from "../components/layout/SearchHeader";
import { FilterBar } from "../components/filters/FilterBar";
import { ListingsPanel } from "../components/listings/ListingsPanel";
import { PropertyMarker } from "../components/map/PropertyMarker";
import { ScoreLayer } from "../components/map/ScoreLayer";
import { AreaMarker } from "../components/map/AreaMarker";
import { LayerToggle } from "../components/map/LayerToggle";
import { useSearchState } from "../hooks/useSearchState";
import { useAreas } from "../hooks/useAreas";
import { AreaScoreOutput } from "../types/api";
import { ScoreType } from "../lib/colourScales";
import { AREA_SCORES_MOCK, MOCK_PROPERTIES } from "../data/mockData";

const DUBLIN_CENTER = { lat: 53.3498, lng: -6.2603 };

function getCentroid(geometry: any): { lat: number; lng: number } | null {
  if (!geometry?.coordinates) return null;
  try {
    let coords = geometry.coordinates;
    if (geometry.type === "MultiPolygon") coords = coords[0][0];
    else if (geometry.type === "Polygon") coords = coords[0];
    if (!coords?.length || !Array.isArray(coords[0])) return null;
    const sumLat = coords.reduce((s: number, [_, lat]: number[]) => s + lat, 0);
    const sumLng = coords.reduce((s: number, [lng]: number[]) => s + lng, 0);
    return { lat: sumLat / coords.length, lng: sumLng / coords.length };
  } catch {
    return null;
  }
}

function MapContent({
  selectedId,
  onSelectProperty,
  showChoropleth,
  choroplethType,
}: {
  selectedId: number | null;
  onSelectProperty: (id: number) => void;
  showChoropleth: boolean;
  choroplethType: ScoreType;
}) {
  const map = useMap();
  const [zoom, setZoom] = useState(11);

  useEffect(() => {
    if (!map) return;
    const listener = map.addListener("zoom_changed", () => setZoom(map.getZoom() ?? 11));
    setZoom(map.getZoom() ?? 11);
    return () => google.maps.event.removeListener(listener);
  }, [map]);

  useEffect(() => {
    if (selectedId && map) {
      const property = MOCK_PROPERTIES.find((p) => p.id === selectedId);
      if (property) {
        map.panTo({ lat: property.lat, lng: property.lng });
        if (map.getZoom()! < 15) map.setZoom(15);
      }
    }
  }, [selectedId, map]);

  return (
    <>
      {showChoropleth && <ScoreLayerWrapper choroplethType={choroplethType} />}
      {showChoropleth && <ReviewMarkersWrapper />}

      {MOCK_PROPERTIES.map((p) => (
        <PropertyMarker
          key={p.id}
          property={p}
          isSelected={selectedId === p.id}
          zoom={zoom}
          onClick={() => onSelectProperty(p.id)}
        />
      ))}
    </>
  );
}

function ScoreLayerWrapper({ choroplethType }: { choroplethType: ScoreType }) {
  const { data: areas } = useAreas();

  const mockScores = React.useMemo(() => {
    const cache: Record<number, AreaScoreOutput> = {};
    Object.entries(AREA_SCORES_MOCK).forEach(([areaId, scores]) => {
      cache[Number(areaId)] = {
        area_id: Number(areaId),
        affordability_score: scores.affordability,
        safety_score: scores.safety,
        livability_score: scores.livability,
        livability_confidence: null,
        needs_human_review: scores.needs_human_review,
        agent_summary: null,
        model_versions_used: {},
        last_updated: new Date().toISOString(),
      };
    });
    return cache;
  }, []);

  if (!areas || areas.length === 0) return null;

  return (
    <ScoreLayer
      areas={areas}
      activeScoreType={choroplethType}
      scoresCache={mockScores}
      onAreaClick={() => {}}
    />
  );
}

function ReviewMarkersWrapper() {
  const { data: areas } = useAreas();
  if (!areas) return null;

  return (
    <>
      {areas
        .map((area: any) => {
          const scores = AREA_SCORES_MOCK[area.id as number];
          if (scores?.needs_human_review) {
            const centroid = getCentroid(area.geometry);
            if (centroid) {
              return (
                <AreaMarker
                  key={area.id}
                  position={centroid}
                  needsReview={true}
                  onClick={() => {}}
                />
              );
            }
          }
          return null;
        })
        .filter(Boolean)}
    </>
  );
}

export function SearchPage() {
  const state = useSearchState();
  const [searchParams] = useSearchParams();
  const locationQuery = searchParams.get("location") || "";
  const [showChoropleth, setShowChoropleth] = useState(false);
  const [choroplethType, setChoroplethType] = useState<ScoreType>("price");

  const hasActiveFilters =
    !!state.filters.minPrice ||
    !!state.filters.maxPrice ||
    !!state.filters.propertyType;

  const mapPanel = (
    <div className="w-full h-full relative">
      {showChoropleth && (
        <LayerToggle activeLayer={choroplethType} onChange={setChoroplethType} />
      )}
      <button
        onClick={() => setShowChoropleth(!showChoropleth)}
        className={`absolute top-3 right-3 z-10 px-3 py-1.5 rounded-lg text-xs font-semibold shadow-md transition-all ${
          showChoropleth
            ? "bg-indigo-600 text-white border border-indigo-600"
            : "bg-white text-gray-700 hover:bg-gray-50 border border-gray-300"
        }`}
      >
        {showChoropleth ? "Scores On" : "Scores"}
      </button>
      <Map
        defaultCenter={DUBLIN_CENTER}
        defaultZoom={11}
        style={{ height: "100%", width: "100%" }}
        gestureHandling="greedy"
        disableDefaultUI={false}
        zoomControl={true}
      >
        <MapContent
          selectedId={state.selectedPropertyId}
          onSelectProperty={state.setSelectedPropertyId}
          showChoropleth={showChoropleth}
          choroplethType={choroplethType}
        />
      </Map>
    </div>
  );

  const listPanel = (
    <>
      <SearchHeader
        propertyCount={state.filteredCount}
        onClearFilters={state.clearFilters}
        hasActiveFilters={hasActiveFilters}
        onAskAI={() => {
          const event = new CustomEvent("open-chat-widget");
          window.dispatchEvent(event);
        }}
      />
      {locationQuery && (
        <div className="px-5 py-2 bg-indigo-50 border-b border-indigo-100 text-sm text-indigo-700">
          Searching in: <span className="font-semibold">{locationQuery}</span>
        </div>
      )}
      <FilterBar
        filters={state.filters}
        sortBy={state.sortBy}
        onFiltersChange={state.setFilters}
        onSortChange={state.setSortBy}
      />
      <ListingsPanel
        properties={state.pagedProperties}
        filteredCount={state.filteredCount}
        page={state.page}
        totalPages={state.totalPages}
        selectedPropertyId={state.selectedPropertyId}
        onSelectProperty={state.setSelectedPropertyId}
        onLoadMore={() => state.setPage(state.page + 1)}
      />
    </>
  );

  return (
    <div className="h-screen w-full flex flex-col">
      <SiteHeader />
      <SplitLayout mapPanel={mapPanel} listPanel={listPanel} />
    </div>
  );
}
