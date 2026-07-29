---
name: testing-trace
description: End-to-End Testing & Trace Guidelines.
---

# End-to-End Testing & Trace Guidelines

When testing or verifying the TerraPulse pipeline, use the following integration trace model to ensure all layers communicate correctly.

## Trace Example: Dublin 1 (`area_id = 1`)
1. **Ingestion & Storage**:
   - Verify `areas` geometry (POLYGON).
   - Check `property_sales`, `amenities`, `crime_stats`, and `area_demographics` for the area ID.
2. **Agents Layer**:
   - Check `area_agent_summaries`.
   - Verify if `needs_human_review` is set (e.g., if qualitative sentiment on safety contradicts objective amenity counts).
3. **Models Layer**:
   - Verify formulas are correctly applied for Affordability and Safety using the active model registry version.
   - Verify Price Prediction (LightGBM) output.
4. **Backend Layer**:
   - `GET /v1/areas/{id}/score` must return the aggregated JSON exactly matching the Pydantic contract.
   - Verify `needs_human_review: true` passes through unmodified.
5. **Frontend Layer**:
   - **Map View**: Must render polygon via `/v1/areas` GeoJSON and show Warning icon (`AreaMarker.tsx`) if `needs_human_review` is true.
   - **Detail Panel**: `AreaDetailPanel.tsx` must prominently display `ReviewFlagBanner.tsx` and the Price Predictor Widget.

**Crucial Check**: The review gate rule must successfully traverse from Agents -> DB -> Backend -> Frontend without degradation or silent drops.
