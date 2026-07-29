import React, { useState, useEffect, useMemo } from "react";
import { MapContainer, TileLayer, ZoomControl, useMap, useMapEvents } from "react-leaflet";
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
import { getCentroid, jitterCentroid } from "../lib/geo";

const DUBLIN_CENTER: [number, number] = [53.3498, -6.2603];
const LIGHT_TILE_URL = "https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png";

type SearchProperty = { id: number; lat: number | null; lon: number | null; price_eur: number; area_id: number; area_name: string | null; address_raw: string; sale_date: string; property_type: string | null };

function MapContent({
  properties,
  selectedId,
  onSelectProperty,
  showChoropleth,
  choroplethType,
}: {
  properties: SearchProperty[];
  selectedId: number | null;
  onSelectProperty: (id: number) => void;
  showChoropleth: boolean;
  choroplethType: ScoreType;
}) {
  const map = useMap();
  const [zoom, setZoom] = useState(11);
  const { data: areas } = useAreas();

  // The PPR dataset backing this app has no per-property lat/lon (see
  // README's ingestion issues) - fall back to the property's area centroid
  // (jittered so properties in the same area don't stack into one dot)
  // rather than silently dropping the marker entirely.
  const areaCentroids = useMemo(() => {
    const map: Record<number, [number, number]> = {};
    (areas ?? []).forEach((a: any) => {
      const c = getCentroid(a.geometry);
      if (c) map[a.id] = c;
    });
    return map;
  }, [areas]);

  const plottable = useMemo(
    () =>
      properties
        .map((p) => {
          if (p.lat && p.lon) return { property: p, position: [p.lat, p.lon] as [number, number], approximate: false };
          const centroid = areaCentroids[p.area_id];
          if (!centroid) return null;
          return { property: p, position: jitterCentroid(centroid, p.id), approximate: true };
        })
        .filter((x): x is { property: SearchProperty; position: [number, number]; approximate: boolean } => x !== null),
    [properties, areaCentroids]
  );

  useMapEvents({
    zoomend: () => setZoom(map.getZoom()),
  });

  useEffect(() => {
    if (selectedId) {
      const entry = plottable.find((p) => p.property.id === selectedId);
      if (entry) {
        map.panTo(entry.position);
        if (map.getZoom() < 15) map.setZoom(15);
      }
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedId]);

  return (
    <>
      {showChoropleth && <ScoreLayerWrapper choroplethType={choroplethType} />}

      {plottable.map(({ property: p, position, approximate }) => (
        <PropertyMarker
          key={p.id}
          property={{ ...p, lat: position[0], lon: position[1] }}
          isSelected={selectedId === p.id}
          zoom={zoom}
          approximate={approximate}
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
    !!state.filters.minPrice ||
    !!state.filters.maxPrice ||
    !!state.filters.areaId ||
    !!state.filters.soldAfter ||
    !!state.filters.soldBefore;

  const filterState: FilterState = state.filters;

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
        zoomControl={false}
        style={{ height: "100%", width: "100%", background: "#020617" }}
      >
        <ZoomControl position="bottomright" />
        <TileLayer
          url={LIGHT_TILE_URL}
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
