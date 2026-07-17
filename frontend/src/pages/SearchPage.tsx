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
import { LayerToggle } from "../components/map/LayerToggle";
import { useSearchState } from "../hooks/useSearchState";
import { useAreas } from "../hooks/useAreas";
import { FilterState, SortOption } from "../hooks/useSearchState";
import { ScoreType } from "../lib/colourScales";

const DUBLIN_CENTER = { lat: 53.3498, lng: -6.2603 };

function MapContent({
  properties,
  selectedId,
  onSelectProperty,
  showChoropleth,
  choroplethType,
}: {
  properties: { id: number; lat: number | null; lon: number | null; price_eur: number; area_id: number; area_name: string | null; address_raw: string; sale_date: string; property_type: string | null }[];
  selectedId: number | null;
  onSelectProperty: (id: number) => void;
  showChoropleth: boolean;
  choroplethType: ScoreType;
}) {
  const map = useMap();
  const [zoom, setZoom] = useState(11);

  useEffect(() => {
    if (!map) return;
    const listener = map.addListener("zoom_changed", () =>
      setZoom(map.getZoom() ?? 11)
    );
    setZoom(map.getZoom() ?? 11);
    return () => google.maps.event.removeListener(listener);
  }, [map]);

  useEffect(() => {
    if (selectedId && map) {
      const property = properties.find((p) => p.id === selectedId);
      if (property && property.lat && property.lon) {
        map.panTo({ lat: property.lat, lng: property.lon });
        if (map.getZoom()! < 15) map.setZoom(15);
      }
    }
  }, [selectedId, map, properties]);

  return (
    <>
      {showChoropleth && <ScoreLayerWrapper choroplethType={choroplethType} />}

      {properties
        .filter((p) => p.lat && p.lon)
        .map((p) => (
          <PropertyMarker
            key={p.id}
            property={{ ...p, lat: p.lat!, lon: p.lon! }}
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
  if (!areas || areas.length === 0) return null;

  return (
    <ScoreLayer
      areas={areas}
      activeScoreType={choroplethType}
      scoresCache={{}}
      onAreaClick={() => {}}
    />
  );
}

export function SearchPage() {
  const state = useSearchState();
  const [searchParams] = useSearchParams();
  const locationQuery = searchParams.get("location") || "";
  const [showChoropleth, setShowChoropleth] = useState(false);
  const [choroplethType, setChoroplethType] = useState<ScoreType>("price");

  const hasActiveFilters =
    !!state.filters.minPrice || !!state.filters.maxPrice;

  const filterState: FilterState = {
    minPrice: state.filters.minPrice,
    maxPrice: state.filters.maxPrice,
  };

  const mapPanel = (
    <div className="w-full h-full relative">
      {showChoropleth && (
        <LayerToggle
          activeLayer={choroplethType}
          onChange={setChoroplethType}
        />
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
        mapId="DEMO_MAP_ID"
        style={{ height: "100%", width: "100%" }}
        gestureHandling="greedy"
        disableDefaultUI={false}
        zoomControl={true}
      >
        <MapContent
          properties={state.properties}
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
          Searching in:{" "}
          <span className="font-semibold">{locationQuery}</span>
        </div>
      )}
      <FilterBar
        filters={filterState}
        sortBy={state.sortBy}
        onFiltersChange={(f) => state.setFilters(f)}
        onSortChange={state.setSortBy}
      />
      <ListingsPanel
        properties={state.properties}
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
