import React, { useState, useEffect } from "react";
import { MapContainer, TileLayer, useMap, useMapEvents } from "react-leaflet";
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

const DUBLIN_CENTER: [number, number] = [53.3498, -6.2603];
const DARK_TILE_URL = "https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png";

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

  useMapEvents({
    zoomend: () => setZoom(map.getZoom()),
  });

  useEffect(() => {
    if (selectedId) {
      const property = properties.find((p) => p.id === selectedId);
      if (property && property.lat && property.lon) {
        map.panTo([property.lat, property.lon]);
        if (map.getZoom() < 15) map.setZoom(15);
      }
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedId]);

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
        className={`absolute top-3 right-3 z-[1000] px-3 py-1.5 rounded-lg text-xs font-semibold shadow-md transition-all ${
          showChoropleth
            ? "bg-violet-500 text-white border border-violet-500"
            : "bg-slate-900/90 backdrop-blur text-slate-300 hover:bg-slate-800 border border-slate-700"
        }`}
      >
        {showChoropleth ? "Scores On" : "Scores"}
      </button>
      <MapContainer
        center={DUBLIN_CENTER}
        zoom={11}
        scrollWheelZoom
        style={{ height: "100%", width: "100%", background: "#020617" }}
      >
        <TileLayer
          url={DARK_TILE_URL}
          attribution='&copy; <a href="https://carto.com/attributions">CARTO</a> &copy; OpenStreetMap contributors'
        />
        <MapContent
          properties={state.properties}
          selectedId={state.selectedPropertyId}
          onSelectProperty={state.setSelectedPropertyId}
          showChoropleth={showChoropleth}
          choroplethType={choroplethType}
        />
      </MapContainer>
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
        <div className="px-5 py-2 bg-violet-500/10 border-b border-violet-500/20 text-sm text-violet-300">
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
    <div className="h-screen w-full flex flex-col bg-slate-950">
      <SiteHeader />
      <SplitLayout mapPanel={mapPanel} listPanel={listPanel} />
    </div>
  );
}
