# AGENTS.md — Phase 6: Provider Migration Verification & Hardening

This extends Phases 1-5. Two significant swaps just happened: the agent layer's LLM
client moved from the Anthropic SDK to the OpenAI SDK (targeting OpenRouter/Groq,
open-source models), and the frontend's map moved from Google Maps to Leaflet+OSM. The
goal of removing API key dependencies is good and worth keeping. This phase exists
because a provider swap of this size touches contracts that were written assuming the
old providers' specific behaviour — find and fix what those swaps quietly broke before
building anything new on top of them.

**This phase verifies and hardens. It does not add new features.** If you find a real
gap that needs new code (e.g. a retry strategy that didn't exist before), write the
minimum needed to close it, and tell me clearly what was missing and why.

---

## 1. LLM client migration — what to verify

### 1.1 Structured output reliability (the biggest real risk)
Open-source models served via OpenRouter/Groq are generally less reliable than Claude at
returning strict, schema-valid JSON on the first try — this was a soft assumption baked
into Phases 2 and 3 ("retry once, then dead-letter") when the underlying model was
Claude. Re-verify this assumption is still good enough, or tighten it:

- Run the Phase 2 extract/score steps against the actual model now configured (whichever
  specific OpenRouter/Groq model was chosen — name it explicitly in your report to me)
  across a reasonable sample (e.g. 20-30 real text inputs already in the dataset) and
  report: what % pass schema validation on the first attempt, what % pass after the
  existing one retry, what % end up dead-lettered.
- If first-attempt pass rate is materially worse than it likely was with Claude, do ONE
  of the following — pick the smallest fix that gets reliability back to an acceptable
  level (define "acceptable" as >90% reaching valid output within the existing retry
  budget), and tell me which you chose and why:
  - Tighten the prompt's JSON-only instruction (some open models respond better to
    explicit few-shot examples of the exact schema than Claude needed)
  - Check whether the chosen OpenRouter/Groq model supports a native "JSON mode" or
    function-calling/tool-use parameter — if so, use it instead of relying purely on
    prompt instructions, since constrained decoding is much more reliable than
    instruction-following alone
  - If neither closes the gap, increase the retry budget from 1 to 2, but log this
    explicitly as a cost/latency tradeoff in `docs/architecture.md`
- Do NOT silently lower the bar by loosening the Pydantic schema to accept more
  permissive output — the schema represents what Phase 3 and Phase 4 actually need
  downstream; loosening it just moves the failure further down the pipeline.

### 1.2 Model traceability fields
`ModelMetadata.model_name` (Phase 3) and any place Phase 2 logs `model_name` per
`area_agent_summaries` row need to now log the REAL model identifier from the new
provider (e.g. the actual OpenRouter model slug, not a leftover "claude-..." string from
before the migration). Check every place a model name is logged or displayed (including
the frontend's `PricePredictorWidget` model-version display from Phase 4) and confirm
none of them still reference Anthropic model names as a stale default or fallback value.

### 1.3 Error handling differences
The OpenAI SDK's error types, rate-limit behaviour, and timeout defaults differ from the
Anthropic SDK's. Re-check `agents_layer/llm_client.py`'s retry-on-transient-error logic
(built in Phase 2) actually catches the right exception types for the OpenAI SDK, not
leftover Anthropic exception handling that now silently fails to catch anything.

### 1.4 Cost/rate-limit behaviour
Free tiers on OpenRouter/Groq typically have tighter rate limits than a paid Anthropic
key. Check whether `run_agent_pipeline.py`'s batch processing (Phase 2) needs throttling
added to stay within the new provider's free-tier limits, and report what those limits
actually are for whichever provider/model was chosen.

---

## 2. Frontend mapping migration — what to verify

### 2.1 Component-level re-check against Phase 4's spec
Confirm each of these still does what Phase 4 specified, now on Leaflet instead of
Google Maps:

- `MapContainer.tsx` — mounts a Leaflet map with an OSM tile layer; confirm tile
  attribution is correctly displayed (OSM's licence requires visible attribution — check
  it's actually showing, this is a real licence requirement, not just a nice-to-have)
- `ScoreLayer.tsx` — choropleth rendering via Leaflet's GeoJSON layer with a `style`
  function driven by score value, NOT a re-implementation of the colour-scale logic;
  confirm `lib/colourScales.ts` from Phase 4 is still the single source of colour logic,
  reused as-is, not duplicated for Leaflet
- `AreaMarker.tsx` — Leaflet markers/popups instead of Google Maps markers; confirm
  click-to-open-detail-panel behaviour still works identically to Phase 4's spec
- The `needs_human_review` warning marker (Phase 4, Section 4) — confirm this still
  renders distinctly and visibly on the Leaflet map; this is the project's headline
  feature and migrations are exactly when such details get silently dropped — check it
  explicitly, do not assume it carried over
- Null-score "no data" area styling (Phase 4, Section 5) — confirm still distinct from
  zero and from missing areas under Leaflet's styling model

### 2.2 GeoJSON handoff
Phase 5 had the backend serving PostGIS geometry as GeoJSON specifically for Google
Maps' choropleth rendering. Leaflet consumes GeoJSON natively, so this should mostly
just work — but confirm the GeoJSON the backend serves doesn't have any Google-Maps-
specific formatting assumptions baked in (e.g. coordinate order — GeoJSON spec is
[longitude, latitude], confirm the backend wasn't accidentally serving
[latitude, longitude] to match something Google Maps tolerated but Leaflet won't).

### 2.3 Config and key cleanup
Since the explicit goal was removing API key dependencies:
- Remove `VITE_GOOGLE_MAPS_KEY` from `.env.example` and any code that reads it
- Confirm `npm run build` and `npm run dev` genuinely require zero API keys end-to-end
  now, as claimed — verify by actually running both from a `.env` with only DB/backend
  config and no map/LLM keys, and report if anything still silently expects one
- Update `README.md`'s prerequisites section (Phase 5) to remove the Google Maps API key
  requirement and add whatever OpenRouter/Groq key (if any is still needed — some Groq
  free tier usage requires a free API key even if there's no cost) is now required instead

---

## 3. Re-run the Phase 5 integration checks that this migration could have broken

Specifically re-verify these two from Phase 5's list, since they're the ones most likely
disturbed by today's changes:

- **Contract drift check**: re-diff `frontend/src/types/api.ts` against
  `shared/model_contract.py` — confirm `model_name`/`model_version` typing didn't drift
  when the restored Vite/React config files were added back.
- **Review-gate end-to-end check**: confirm, live, in the running app, that an area with
  `needs_human_review = true` still produces a visible warning marker on the new Leaflet
  map and a banner in the detail panel. State explicitly in your report whether you
  verified this with a real flagged area or a manually seeded test case.

---

## 4. What "done" looks like for this phase

- [ ] Structured-output pass rate for the new LLM provider is measured and reported
      (Section 1.1), with a concrete fix applied if the rate was poor
- [ ] No stale Anthropic model name strings remain anywhere in logs, defaults, the
      database, or the frontend display (Section 1.2)
- [ ] `llm_client.py`'s error handling correctly matches OpenAI SDK exception types
      (Section 1.3)
- [ ] New provider's rate limits are documented and respected by the batch pipeline
      (Section 1.4)
- [ ] OSM tile attribution is visibly displayed on the map (licence requirement)
- [ ] Colour scale logic confirmed still single-sourced, not duplicated for Leaflet
- [ ] The `needs_human_review` warning marker is confirmed visible on the live Leaflet
      map for a real or seeded flagged area
- [ ] GeoJSON coordinate order confirmed correct for Leaflet (lon, lat)
- [ ] `npm run dev` and `npm run build` confirmed to require zero API keys, verified by
      an actual run with a stripped `.env`
- [ ] `.env.example` and `README.md` updated to reflect the real, current key
      requirements (likely: none for maps, possibly one free-tier key for the LLM
      provider)
- [ ] `docs/architecture.md` updated: replace references to Anthropic/Google Maps with
      the actual current providers, and add a short "why we moved to free/open-source
      providers" note since this is a legitimate, explainable design decision worth
      documenting rather than hiding

---

## 5. Working agreement

- If structured-output reliability from the new LLM provider is poor even after the
  fixes in Section 1.1, stop and tell me the actual pass-rate numbers rather than quietly
  shipping a degraded agent layer — this is a real quality tradeoff of the free-model
  decision and I should know the size of it.
- If the OSM/Leaflet licence attribution requirement conflicts with any UI design
  decision from Phase 4, keep the attribution and adjust the design — this is a real
  legal requirement, not a style preference.
- Report back which specific OpenRouter/Groq model and which specific map tile provider
  ended up configured — these decisions should be explicit and known, not buried in a
  default config value nobody chose deliberately.