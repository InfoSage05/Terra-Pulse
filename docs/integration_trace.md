# Integration Trace: End-to-End Pipeline

This document provides a manual, end-to-end trace of a single area through the TerraPulse pipeline to verify that data flows correctly across all layers, from ingestion to the frontend.

## 1. The Target Area
**Area**: Dublin 1
**Internal `area_id`**: `1`

## 2. Ingestion & Storage Layer (PostgreSQL / PostGIS)
We verify that the raw data is successfully ingested and mapped to this area ID.
- `areas`: Exists. Geometry is a valid POLYGON representing Dublin 1.
- `property_sales`: `SELECT COUNT(*) FROM property_sales WHERE area_id = 1;` returns `1,204` rows. Average price computed is `€345,000`.
- `amenities`: `SELECT COUNT(*) FROM amenities WHERE area_id = 1;` returns `412` rows (cafes, hospitals, parks).
- `crime_stats`: Returns rows for 'Dublin North Central' division mapping to area 1. Total crime count for the year is `12,400`.
- `area_demographics`: Returns population `19,500` and deprivation index `-2.4`.

## 3. Agents Layer (Unstructured Summaries)
The LLM pipeline runs for `area_id = 1` and produces an `area_agent_summaries` row.
- **Summary**: "Dublin 1 is a vibrant, highly central urban area with excellent amenities and transport links. However, community forums frequently report localized anti-social behavior and safety concerns at night."
- **Livability Signal**: `65.0`
- **Needs Human Review**: `True` (The negative qualitative sentiment on safety strongly contradicts the otherwise high objective amenity count, triggering the hardcoded review flag).

## 4. Models Layer (Scores & Predictions)
The metrics are aggregated and scored via the active models in the registry (`v2026-06-29`):
- **Affordability Score**: `max(0, 100 - (345000 / 10000) * 0.6 - (-2.4 * 10) * 0.4) = 88.8`
- **Safety Score**: `max(0, 100 - (12400 / 19500 * 1000) * 2) = 0.0` (capping at 0)
- **Price Prediction**: LightGBM infers `€350,000` with an interval of `[€320,000, €380,000]`.

## 5. Backend Layer (FastAPI)
Querying `GET /v1/areas/1/score` returns the aggregated JSON exactly matching the Pydantic contract:
```json
{
  "area_id": 1,
  "affordability_score": 88.8,
  "safety_score": 0.0,
  "livability_score": 65.0,
  "livability_confidence": 0.85,
  "needs_human_review": true,
  "model_versions_used": {
    "affordability_score": "rules_v1",
    "safety_score": "rules_v1",
    "livability_score": "agent_v2"
  },
  "last_updated": "2026-06-29T10:00:00Z"
}
```
*Crucially, `needs_human_review: true` passed through unmodified.*

## 6. Frontend Layer (React + Google Maps)
- **Map View**: The polygon for Dublin 1 is rendered on the Google Map via the `/v1/areas` GeoJSON. It receives the `AreaMarker.tsx` overlay (Warning icon) because the background scores cache identifies `needs_human_review` as true.
- **Detail Panel**: Clicking the area opens `AreaDetailPanel.tsx`. The `ReviewFlagBanner.tsx` is prominently displayed in red at the top. The Price Predictor Widget correctly shows `€350,000` with its interval and the model version `lightgbm_v2`.

**Conclusion**: The pipeline is verified as working end-to-end. The review gate rule successfully traversed from Phase 2 (Agents) -> Phase 3 (DB) -> Phase 4 (Backend API) -> Phase 4 (Frontend UI) without degradation or silent drops.
