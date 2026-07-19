import React from "react";
import { useNavigate } from "react-router-dom";
import { MapContainer, TileLayer, CircleMarker } from "react-leaflet";
import { ArrowRight, Map as MapIcon } from "lucide-react";
import { useAreas } from "../../hooks/useAreas";
import { getCentroid } from "../../lib/geo";

const DUBLIN_CENTER: [number, number] = [53.3498, -6.2603];
const DARK_TILE_URL = "https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png";

export function MapPreviewStrip() {
  const navigate = useNavigate();
  const { data: areas } = useAreas();

  return (
    <section className="max-w-6xl mx-auto px-6 py-12">
      <div className="relative rounded-2xl overflow-hidden" style={{ height: 320 }}>
        <div className="absolute inset-0 pointer-events-none">
          <MapContainer
            center={DUBLIN_CENTER}
            zoom={12}
            zoomControl={false}
            dragging={false}
            scrollWheelZoom={false}
            doubleClickZoom={false}
            touchZoom={false}
            boxZoom={false}
            keyboard={false}
            attributionControl={false}
            style={{ height: "100%", width: "100%", background: "#020617" }}
          >
            <TileLayer url={DARK_TILE_URL} />
            {areas?.map((area: any) => {
              const centroid = getCentroid(area.geometry);
              if (!centroid) return null;
              return (
                <CircleMarker
                  key={area.id}
                  center={centroid}
                  radius={5}
                  pathOptions={{
                    color: "#a78bfa",
                    fillColor: "#8b5cf6",
                    fillOpacity: 0.9,
                    weight: 1.5,
                  }}
                />
              );
            })}
          </MapContainer>
        </div>

        {/* Gradient scrim + CTA */}
        <div className="absolute inset-0 bg-gradient-to-t from-slate-950 via-slate-950/40 to-transparent flex items-end justify-center pb-8">
          <div className="bg-slate-900/90 backdrop-blur border border-slate-700 rounded-2xl px-6 py-4 text-center shadow-xl">
            <p className="font-display text-lg font-semibold text-slate-50 flex items-center justify-center gap-2">
              <MapIcon className="w-5 h-5 text-violet-400" aria-hidden="true" />
              Explore the full map
            </p>
            <p className="text-sm text-slate-400 mt-1">Price · Safety · Livability</p>
            <button
              onClick={() => navigate("/map")}
              className="mt-3 inline-flex items-center gap-1.5 bg-violet-500 hover:bg-violet-600 text-white text-sm font-medium px-4 py-2 rounded-lg transition-colors"
            >
              Open Interactive Map
              <ArrowRight className="w-4 h-4" aria-hidden="true" />
            </button>
          </div>
        </div>
      </div>
    </section>
  );
}
