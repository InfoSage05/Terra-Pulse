# AGENTS.md — Phase 7: Zillow-Style UI + Full Stack Verification

## CRITICAL: Read this before writing a single line of code

The frontend has never successfully connected to a real backend with real data. Docker is
not installed on the development machine. Postgres has never run. The backend has never
served a real API response. Before building any new UI, you must get the full stack
actually running and verified. A Zillow-style frontend connected to nothing is worthless.
Do the steps in Section 0 first, completely, before touching any frontend code.

---

## 0. Get the stack running — mandatory gate before any UI work

### 0.1 Install Docker Desktop
Docker Desktop must be installed and running before anything else.
- Download: https://www.docker.com/products/docker-desktop/
- Run the installer, accept WSL 2, restart the machine when prompted
- After restart, open Docker Desktop and wait for the engine to fully start
- Verify in a new terminal:
```bash
docker --version
docker compose version
```
Both must return version strings, not errors. Do not proceed past this point until
they do.

### 0.2 Start the database
From the repo root:
```bash
docker compose up -d postgres redis
docker compose ps
```
`postgres` must show as `healthy` before proceeding. If it shows `starting` or
`unhealthy`, check logs:
```bash
docker compose logs postgres
```
Fix any issues (missing env vars in `.env`, port conflicts, etc.) before moving on.

### 0.3 Run migrations and seed areas
```bash
docker compose exec postgres psql -U ${POSTGRES_USER} -d ${POSTGRES_DB} -f /dev/stdin < storage/migrations/001_init_postgis.sql
# ... run migrations 002 through 007 in order
python storage/seeds/seed_areas.py
```
Then verify real rows exist:
```bash
docker compose exec postgres psql -U ${POSTGRES_USER} -d ${POSTGRES_DB} -c "SELECT id, name, area_type FROM areas LIMIT 10;"
```
If this returns 0 rows, seed_areas.py did not work — fix it before continuing.

### 0.4 Run ingestion for at least one real source
At minimum, run the PPR connector to get real property_sales rows:
```bash
python ingestion/jobs/run_ingestion.py --source ppr
```
Verify:
```bash
docker compose exec postgres psql -U ${POSTGRES_USER} -d ${POSTGRES_DB} -c "SELECT count(*) FROM property_sales;"
```
Must return a non-zero count. If it returns 0, the connector did not write data —
check dead_letter logs and fix before continuing.

### 0.5 Start and verify the backend
```bash
python -m uvicorn backend.app.main:app --reload --port 8000
```
Then confirm these three endpoints return real data (not errors, not empty arrays):
- `GET http://localhost:8000/v1/areas` — must return a list of area objects
- `GET http://localhost:8000/v1/areas/1` — must return a single area with real fields
- `GET http://localhost:8000/v1/areas/1/score` — may return null score fields if
  models haven't run yet, but must not return a 404 or 500

**Do not start Section 1 until all three of these return real, non-error responses.**
Report exactly what each returns before moving forward.

### 0.6 Add the property listings endpoint (new backend work)
The Zillow-style UI requires a property listings feed — individual properties with
price, address, beds/baths, property type — not just area-level aggregates. Check
whether `GET /v1/properties` exists already. If not, add it now in
`backend/app/api/v1/properties.py`:

```python
# GET /v1/properties
# Query params: area_id (optional), min_price, max_price, property_type, limit, offset
# Returns: paginated list of PropertyListing objects from property_sales table
# Each item: id, area_id, address_raw, price_eur, sale_date, property_type (if available)
```

Add the corresponding Pydantic response model to `shared/model_contract.py`:
```python
class PropertyListing(BaseModel):
    id: int
    area_id: int
    address_raw: str
    price_eur: float
    sale_date: str
    property_type: str | None
    lat: float | None
    lon: float | None
```

This endpoint is what powers the right-side property list in the UI. Verify it returns
real rows before moving to Section 1.

---

## 1. The target UI — what to build

Reference: Zillow.com's search interface. The layout is:
- Left half: interactive map (Leaflet, already built) showing property markers
- Right half: scrollable list of property cards with filters at the top
- The two sides are linked: panning/clicking the map filters the list; clicking a card
  highlights/zooms to that property on the map

This replaces or extends the current `MapPage.tsx`. Do not delete the existing
choropleth score layer functionality — it stays as a toggleable overlay. The new
Zillow-style view is the default landing experience.

---

## 2. Layout structure

```
frontend/src/
├── pages/
│   └── SearchPage.tsx          # new main page replacing or wrapping MapPage
├── components/
│   ├── layout/
│   │   ├── SplitLayout.tsx     # left/right split — map takes 55% width, list 45%
│   │   │                         #   on desktop. On mobile, stacks vertically with a
│   │   │                         #   toggle between map view and list view
│   │   └── SearchHeader.tsx     # top bar: location search input + filter controls
│   ├── map/
│   │   ├── MapContainer.tsx     # extend existing — add PropertyMarker layer
│   │   └── PropertyMarker.tsx   # individual property pin on the map, shows price
│   │                              #   label on the marker itself (like Zillow's red
│   │                              #   price bubbles), highlights on hover/select
│   ├── listings/
│   │   ├── ListingsPanel.tsx    # right-side scrollable panel
│   │   ├── PropertyCard.tsx     # individual card: address, price, sale date,
│   │   │                          #   property type badge, area name — no photos
│   │   │                          #   (we don't have images in our data), clean
│   │   │                          #   text-based card instead
│   │   ├── ListingsCount.tsx    # "X properties found" header above the list,
│   │   │                          #   updates live as filters change
│   │   └── LoadMoreButton.tsx   # pagination — load next page of results,
│   │                              #   do not infinite-scroll (simpler, more reliable)
│   └── filters/
│       ├── FilterBar.tsx        # horizontal filter bar below the search header:
│       │                          #   Price range | Property type | Date range | Sort by
│       ├── PriceRangeFilter.tsx # min/max price inputs
│       ├── PropertyTypeFilter.tsx # dropdown: All / Residential / Apartment / House
│       └── SortControl.tsx      # sort by: Price (low-high) | Price (high-low) |
│                                   #   Most recent | Area score
```

---

## 3. Data flow and state

Use a single `useSearchState` hook that holds:
```typescript
interface SearchState {
  mapBounds: LatLngBounds | null   // current map viewport bounds
  selectedAreaId: number | null
  selectedPropertyId: number | null
  filters: {
    minPrice: number | null
    maxPrice: number | null
    propertyType: string | null
    sortBy: 'price_asc' | 'price_desc' | 'recent' | 'score'
  }
  page: number
}
```

- When `mapBounds` changes (user pans/zooms), re-fetch `/v1/properties` with the new
  bounding box — properties outside the current viewport are not shown in the list
- When a filter changes, reset `page` to 0 and re-fetch
- When a property card is clicked, set `selectedPropertyId`, fly the map to that
  property's coordinates, and highlight its marker
- When a map marker is clicked, set `selectedPropertyId` and scroll the corresponding
  card into view in the list panel
- The map's choropleth score overlay (from Phase 4) is toggled by a layer control in
  the top-right of the map — it coexists with the property markers, it is not replaced
  by them

---

## 4. Map marker behaviour (the Zillow price-bubble pattern)

- Each property visible in the current map bounds gets a marker showing its price
  (e.g. "€320K") as a small pill/bubble label
- Unselected: white background, dark border, small font
- Hovered: slightly larger, shadow
- Selected (clicked): filled dark background, white text
- If more than ~200 markers would appear at the current zoom level, cluster them
  (Leaflet.markercluster) showing a count bubble instead — do not render 2000 individual
  markers at country zoom level, it will freeze the browser
- Properties flagged with `needs_human_review` on their area get a small warning icon
  appended to their price bubble — this preserves the Phase 2/3/4 review-gate
  visibility at the individual property level, not just at the area choropleth level

---

## 5. Property card design (text-based, no photos)

Since our data doesn't include property photos, the card must look intentionally clean
rather than like a broken Zillow card with missing images. Design:

```
┌─────────────────────────────────────┐
│ €320,000                    [Badge] │  ← price prominent, property type badge
│ 14 Griffith Avenue, Dublin 9        │  ← address
│ Dublin 9 · Sold Jan 2024            │  ← area name + sale date
│ ──────────────────────────────────  │
│ Safety 78  Afford. 65  Live. 71     │  ← area scores if available, muted if null
│                          [⚠ Review] │  ← only shown if needs_human_review = true
└─────────────────────────────────────┘
```

- Price is the largest text element
- Area scores shown small at the bottom — pull from the area's `/v1/areas/{id}/score`
  response, cached per area_id (don't re-fetch per card, one fetch per unique area_id
  visible in the current page)
- The `⚠ Review` flag is only shown if `needs_human_review` is true — same rule as
  everywhere else in the project, never hidden

---

## 6. Filter behaviour

- All filters are applied as query parameters to `GET /v1/properties`
- Changing any filter triggers an immediate re-fetch (debounced 300ms for price inputs
  to avoid firing on every keystroke)
- Active filters are visually indicated (filled/highlighted state on filter controls)
- A "Clear all filters" button resets to defaults
- The current filter state should be reflected in the URL query string
  (e.g. `?minPrice=200000&propertyType=house`) so the search is shareable/bookmarkable
  — use React Router's `useSearchParams` for this

---

## 7. What "done" looks like for this phase

- [ ] Section 0 fully complete: Docker running, Postgres healthy, real rows in
      `property_sales` and `areas`, backend `/v1/areas` and `/v1/properties` returning
      real data, not errors — **verified by actually calling the endpoints**, not assumed
- [ ] Split layout renders correctly: map left, listings right, responsive on mobile
- [ ] Property markers show price bubbles on the map for properties in the current
      viewport
- [ ] Clicking a marker scrolls to and highlights the corresponding card in the list
- [ ] Clicking a card flies the map to that property and highlights its marker
- [ ] Filter bar works: price range and property type filter the list and map markers
- [ ] URL reflects filter state — sharing the URL reproduces the same search
- [ ] Area score line in the property card shows real scores (or "—" for null), fetched
      once per unique area_id, not once per card
- [ ] `needs_human_review` warning appears on both the map marker and the property card
      for any flagged property's area — verified with a real or seeded flagged case
- [ ] Choropleth score overlay still toggleable and functional alongside the new
      property markers
- [ ] `ListingsCount` updates correctly when filters change or map is panned
- [ ] No browser freeze at low zoom levels — marker clustering kicks in above ~200
      visible markers

---

## 8. Working agreement

- Do not start Section 1 until Section 0 is verified complete with real data. Report
  the actual output of each verification step before proceeding. This is non-negotiable
  — a beautiful UI on top of a broken backend is not progress.
- If `/v1/properties` doesn't exist yet and needs to be added (Section 0.6), fix the
  backend first and confirm it returns real rows before building the frontend against it.
- Do not add property photos or image placeholders — we don't have image data, and a
  deliberately clean text-based card is better than broken image elements.
- If marker clustering library (Leaflet.markercluster) causes any Vite/TypeScript
  import issues, tell me before spending time fighting it — there are known type-
  definition workarounds for this library.
- Report the Section 0 verification results to me before writing any Section 1 code.