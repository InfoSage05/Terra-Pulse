# AGENTS.md — Phase 4: Frontend Layer (React + Google Maps)

This extends Phases 1-3. By now: Postgres is fully populated, the agent pipeline flags
contradictions, a LightGBM model serves real-time price predictions, and FastAPI serves
`/v1/areas`, `/v1/areas/{id}`, `/v1/areas/{id}/score`, and `/v1/predict/price` — all
versioned, all carrying model version info, and `needs_human_review` always passes
through unmodified from Phase 2.

**This phase builds ONLY the Frontend layer.** Do not modify `backend/`, `models_layer/`,
`agents_layer/`, `ingestion/`, or `storage/`. If an endpoint doesn't return what this
phase needs, stop and tell me — do not add backend code from this phase's prompt.

---

## 1. What "done" looks like, stated up front

A user opens the app, sees a map of Dublin areas colour-coded by a score they can switch
between (price / affordability / safety / livability), clicks an area, sees its detail
panel with real numbers and the agent-generated summary, and — critically — if that
area's `needs_human_review` is `true`, sees a visible, unmissable indicator that the
livability read is uncertain or contradicts the data. That last part is not optional
polish; it is the single most important thing this layer has to get right, because it is
the entire payoff of Phases 2 and 3's review-gate work. A frontend that hides this flag
defeats the purpose of building it.

---

## 2. Tech choices (decided, do not relitigate)

- React (Vite), TypeScript — not JavaScript, since the API contract from
  `shared/model_contract.py` should be mirrored as TypeScript types, and that mirroring
  only pays off with type checking.
- Google Maps JavaScript API for the map itself (matches the original project brief).
- No heavy state management library (Redux etc.) — React Query (TanStack Query) for
  server state + plain React state for UI state is enough at this scale.
- Tailwind for styling.
- Do not add authentication/login UI in this phase — out of scope until requested.

---

## 3. Codebase structure

```
frontend/
├── src/
│   ├── types/
│   │   └── api.ts                  # TypeScript interfaces mirroring
│   │                                 #   shared/model_contract.py EXACTLY — field names,
│   │                                 #   optionality (Python `| None` -> TS `| null`),
│   │                                 #   and enums must match. This is the frontend half
│   │                                 #   of the contract discipline from Phase 3 — do not
│   │                                 #   let these drift from the backend's real schema.
│   ├── api/
│   │   ├── client.ts                # fetch wrapper: base URL from env, attaches API
│   │   │                              #   key header, central error handling
│   │   ├── areas.ts                  # getAreas(), getAreaDetail(id), getAreaScore(id)
│   │   └── predict.ts                # predictPrice(input)
│   ├── hooks/
│   │   ├── useAreas.ts                # React Query hook wrapping areas.ts
│   │   ├── useAreaScore.ts            # React Query hook, includes the
│   │   │                                #   needs_human_review field typed as required,
│   │   │                                #   never optional/ignorable in the type
│   │   └── usePricePrediction.ts
│   ├── components/
│   │   ├── map/
│   │   │   ├── MapContainer.tsx        # mounts the Google Map, holds map instance
│   │   │   ├── ScoreLayer.tsx           # renders ONE score type as a choropleth overlay
│   │   │   │                             #   — price / affordability / safety / livability
│   │   │   │                             #   are each an instance of this, swapped via a
│   │   │   │                             #   layer toggle, not four separate components
│   │   │   ├── LayerToggle.tsx          # UI control to switch which ScoreLayer is active
│   │   │   └── AreaMarker.tsx            # click target per area, opens detail panel
│   │   ├── area-detail/
│   │   │   ├── AreaDetailPanel.tsx       # slide-in/side panel shown on area click
│   │   │   ├── ScoreSummaryCard.tsx       # shows the 4 scores + their model versions
│   │   │   ├── ReviewFlagBanner.tsx       # **the most important component in this
│   │   │   │                               #   phase** — renders prominently, unmissable
│   │   │   │                               #   styling (not a small grey badge), when
│   │   │   │                               #   needs_human_review is true. Must explain
│   │   │   │                               #   in plain language that the area's
│   │   │   │                               #   qualitative read and its hard data disagree
│   │   │   │                               #   or that confidence is low — do not just say
│   │   │   │                               #   "flagged," say why, using the `flags` field.
│   │   │   ├── AgentSummaryBlock.tsx       # shows the Phase 2 agent's summary text,
│   │   │   │                               #   confidence, and last-updated date
│   │   │   └── PriceTrendChart.tsx          # simple chart of historical price_sales,
│   │   │                                     #   from area detail endpoint, not from
│   │   │                                     #   the prediction endpoint
│   │   ├── prediction/
│   │   │   └── PricePredictorWidget.tsx     # small form: pick an area, optionally
│   │   │                                     #   property features if the contract
│   │   │                                     #   supports them, calls predictPrice(),
│   │   │                                     #   shows result WITH its confidence
│   │   │                                     #   interval, never just a single number
│   │   ├── filters/
│   │   │   └── AreaFilters.tsx               # basic filter bar (e.g. by area name/type)
│   │   └── shared/
│   │       ├── LoadingState.tsx               # one shared loading component, used
│   │       │                                   #   everywhere data is in flight — no
│   │       │                                   #   silent blank screens
│   │       ├── ErrorState.tsx                  # one shared error component, distinguishes
│   │       │                                   #   "no data yet" (valid, calm message)
│   │       │                                   #   from "request failed" (retry option)
│   │       └── EmptyScoreState.tsx              # specific case: a score field is `null`
│   │                                             #   because no model has scored it yet —
│   │                                             #   per Phase 3, this is valid data, not
│   │                                             #   an error, and must be displayed as
│   │                                             #   "not yet available," not hidden or
│   │                                             #   shown as zero
│   ├── pages/
│   │   └── MapPage.tsx                          # composes MapContainer + AreaDetailPanel
│   │                                              #   + filters into the single main view
│   ├── App.tsx
│   └── main.tsx
├── .env.example                                  # VITE_API_BASE_URL, VITE_GOOGLE_MAPS_KEY
└── tests/
    ├── ReviewFlagBanner.test.tsx                  # explicitly tests that a mocked
    │                                                #   needs_human_review=true API
    │                                                #   response renders the banner —
    │                                                #   mirrors the backend's own
    │                                                #   passthrough test from Phase 3
    ├── EmptyScoreState.test.tsx                     # tests that null score fields render
    │                                                #   as "not available," not as 0 or NaN
    └── PricePredictorWidget.test.tsx
```

---

## 4. Map layer behaviour, specifically

- `ScoreLayer.tsx` takes a `scoreType` prop (`price` | `affordability` | `safety` |
  `livability`) and a colour scale appropriate to that score. Do not hardcode four
  separate colour scales inline in four separate files — define scales once in a
  `lib/colourScales.ts` and reference them.
- Choropleth fill uses the area polygon geometry — if PostGIS geometry isn't yet exposed
  via the API in a frontend-friendly format (e.g. GeoJSON), stop and tell me; do not
  approximate area shapes as circles around a centroid as a silent fallback without
  flagging it to me first, since that's a visible quality regression from "proper
  choropleth."
- Areas with `null` for the currently selected score type render in a distinct neutral
  "no data" colour, never blank/invisible and never falsely colored as if scored zero.
- Areas with `needs_human_review = true` get a visible marker overlay (e.g. a small
  warning icon at the area's center) regardless of which score layer is currently
  selected — this should be visible on the map itself, not only inside the detail panel,
  since a user browsing the map should be able to spot flagged areas before clicking in.

---

## 5. Error and loading state rules

- Every data-fetching hook (`useAreas`, `useAreaScore`, `usePricePrediction`) must
  surface three states to its component: loading, error, success — never assume success.
- A 404 from `/v1/areas/{id}` (area doesn't exist) is a different UI state from a 200
  with `null` score fields (area exists, not yet scored). Do not conflate these.
- Network/server errors show `ErrorState` with a retry action (React Query's `refetch`),
  not a dead end.
- The `PricePredictorWidget` must show the model version that produced a prediction
  (carried in `PricePredictionOutput.model_version`) somewhere in the result, even if
  small — this keeps the "always traceable to a model version" rule from Phase 3 visible
  all the way through to the end user, which is a detail worth having in a viva.

---

## 6. What "done" looks like for this phase

- [ ] `npm run dev` serves the app locally and connects to the real backend from Phase 3
- [ ] Map renders all seeded areas with a working choropleth for at least price and one
      other score type
- [ ] Layer toggle correctly swaps the active score type and its colour scale
- [ ] Clicking an area opens the detail panel with real data from `/v1/areas/{id}` and
      `/v1/areas/{id}/score`
- [ ] `ReviewFlagBanner` renders correctly and visibly for a test area with
      `needs_human_review: true` — verified by `ReviewFlagBanner.test.tsx`, mirroring the
      backend's own passthrough test
- [ ] Null/not-yet-available scores render distinctly from zero and from missing areas
- [ ] `PricePredictorWidget` returns a prediction with a confidence interval and a
      visible model version
- [ ] Loading and error states are visible and distinct in every data-fetching component
      — no blank screens, no infinite spinners with no fallback
- [ ] `frontend/src/types/api.ts` matches `shared/model_contract.py` field-for-field —
      spot check this yourself before marking done
- [ ] `docs/architecture.md` updated with a short section on the frontend's layer
      structure and the review-flag display rule

---

## 7. Working agreement (carried forward)

- If any backend endpoint's actual response shape differs from what Phase 3's contract
  promised, stop and tell me which field is wrong — do not silently adapt the frontend
  type to match a broken backend without flagging the mismatch.
- If PostGIS area geometry isn't available via the API yet in GeoJSON form, stop and ask
  before falling back to centroid circles.
- Do not add login/auth, multi-user features, or payment flows — out of scope.
- Keep `ScoreLayer.tsx` generic across all four score types — if you find yourself
  writing per-score-type conditional branches deep inside it, that's a sign the colour
  scale/data shape abstraction in Section 4 needs fixing, not papering over.