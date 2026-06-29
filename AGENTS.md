# AGENTS.md — Phase 5: Infra, Integration Hardening & Documentation

This extends Phases 1-4. By now: ingestion + storage, the agent pipeline, the
LightGBM/rule-based model layer, the FastAPI backend, and the React+Maps frontend all
work — built phase by phase, each largely in isolation. This phase does NOT add a new
layer. It integrates, hardens, and documents the existing five layers so the whole thing
runs as one system, from a clean clone, in front of someone evaluating it.

**This is the phase that turns five working pieces into one working product.** Do not
add new features to any layer. If you find a real bug while integrating, fix it
minimally and tell me what broke and why — do not refactor beyond the fix.

---

## 1. Why this phase exists

Each layer was built and tested somewhat independently. The most common failure mode at
this point in a multi-phase build is: each layer works on its own, but the seams between
them are untested — e.g. the frontend's TypeScript types silently drifted from the real
backend response, or the agent pipeline's `area_id` type doesn't quite match what the
model layer's feature store expects, or one service assumes the others are already
running and there's no clear startup order. This phase finds and fixes those seams, then
makes the whole thing runnable with one command and documents it so someone unfamiliar
with the build history can run and understand it.

---

## 2. Docker Compose — the full stack, one command

Build `docker-compose.yml` at the repo root (extending whatever Phase 1's Postgres+
PostGIS compose file already had — do not create a second one) with services for:

- `postgres` (PostGIS-enabled, as built in Phase 1)
- `redis` (for score caching, as specified in Phase 3)
- `backend` (FastAPI, built from `backend/Dockerfile` — write this Dockerfile now if it
  doesn't exist yet)
- `frontend` (built from `frontend/Dockerfile` — write this now if it doesn't exist;
  for local dev this can run Vite's dev server, document separately if a production
  static build differs)
- Healthchecks on `postgres` and `redis`, with `backend` waiting on those healthchecks
  before starting (use `depends_on: condition: service_healthy`, not a blind sleep)

Add a `.env.example` at the repo root that is the single source of truth for every env
var across every layer (DB credentials, Google Maps API key, Anthropic API key, model
registry path, etc.) — consolidate any per-layer `.env.example` files that currently
exist into this one, with comments grouping them by layer.

**Explicitly out of scope for this phase:** Kubernetes, cloud deployment configs,
multi-region setup. Docker Compose for local/single-machine running is the target. Note
in `docs/architecture.md` that cloud deployment is a deliberate future step, not done
here.

---

## 3. Integration checks — verify the seams, not the layers

Go through each of the following and report back to me what you find, fixing only clear
bugs (not redesigning):

1. **Contract drift check**: diff `frontend/src/types/api.ts` against
   `shared/model_contract.py` field by field. Report any mismatch before fixing it.
2. **`area_id` type consistency**: confirm the type of `area_id` is consistent across
   `storage/models/db_models.py`, `agents_layer/schemas/fused_summary.py`,
   `shared/model_contract.py`, and `frontend/src/types/api.ts`. This is the single most
   likely place for a silent integer-vs-string or nullable mismatch across five phases.
3. **End-to-end data flow test**: pick ONE real area. Manually trace it through every
   layer — does it have rows in `property_sales`, `amenities`, `crime_stats`? Does it
   have an `area_agent_summaries` row? Does `/v1/areas/{id}/score` return non-null
   values for it? Does it render correctly on the map with real data, not placeholder
   data? Write this trace down in `docs/integration_trace.md` as evidence the pipeline
   genuinely works end-to-end for at least one real case, not just unit-tested in
   isolation.
4. **Cold-start order check**: from a totally fresh `docker-compose up`, with an empty
   database, what is the correct order of operations to get to a working frontend?
   (Migrations → seed areas → run ingestion connectors → run agent pipeline → train
   models → start backend → start frontend, presumably — confirm the real order and
   write it down.) This becomes Section 5 of the README.
5. **Review-gate end-to-end check**: confirm there is at least one real or deliberately
   seeded area where `needs_human_review = true` makes it all the way from the Phase 2
   fuse step, through the Phase 3 API response, to a visibly rendered banner in the
   Phase 4 frontend, right now, in the running system — not just covered by isolated
   unit tests in each phase. This is the project's core differentiator; verify it
   actually works as one continuous path before calling the project done.

---

## 4. CI (lightweight, not a full pipeline)

Add `.github/workflows/ci.yml` that, on every push:
- Spins up Postgres+PostGIS as a service container
- Runs migrations
- Runs the test suites from Phases 1-4 (`ingestion/tests`, `agents_layer/tests`,
  `backend/tests`, `frontend/tests` — whichever exist; don't write new tests in this
  phase, just wire up running the existing ones)
- Lints (whatever linter convention each layer already uses — don't introduce a new one)
- Fails the build on any test failure

Do not add deployment steps to CI in this phase — test-and-lint only.

---

## 5. Documentation pass

### `README.md` (repo root) — rewrite to be complete and standalone
Must include, in order:
1. One-paragraph project description (what TerraPulse is, the Dublin-now/Ireland-later
   scope)
2. Architecture diagram or description (reference `docs/architecture.md`, don't
   duplicate it)
3. Prerequisites (Docker, API keys needed — Google Maps, Anthropic)
4. Exact step-by-step from clean clone to working app — the real order from Section 3.4
5. How to run tests
6. Known limitations (be honest: Dublin-only area coverage so far, crime data at Garda
   division granularity not finer, agent text sources limited to whatever was actually
   scraped, etc. — list what's actually true, not a generic disclaimer)

### `docs/architecture.md` — consolidate, don't fragment
By now this file has likely accumulated notes from each phase. Reorganise it into one
coherent document: one section per layer, in pipeline order, each describing what it
does and how it hands off to the next layer. Include the affordability/safety scoring
formulas (carried over from Phase 3) and the review-gate passthrough rule (carried over
from Phases 2-4) prominently, since these are the project's most distinctive design
decisions.

### `docs/integration_trace.md` (new, from Section 3.3)
The single real area traced end-to-end, with actual values at each layer. This is useful
both as proof-of-correctness and as the easiest thing to walk through in a demo or viva.

---

## 6. What "done" looks like for this phase

- [ ] `docker-compose up` from a clean clone brings up every service in the correct
      order, healthchecked, no manual intervention
- [ ] The cold-start sequence in Section 3.4 is documented and verified to actually work
      from empty
- [ ] Contract drift check (Section 3.1) reported, with any real mismatches fixed
- [ ] `area_id` type consistency (Section 3.2) confirmed across all layers
- [ ] At least one area is traced end-to-end in `docs/integration_trace.md` with real
      values, not placeholders
- [ ] The review-gate end-to-end path (Section 3.5) is confirmed working live, not just
      via isolated unit tests — this is the project's headline feature and must be
      demonstrably true in the running system
- [ ] CI runs on push, runs existing tests across all layers, fails on test failure
- [ ] `README.md` lets a stranger get from clean clone to working app without asking you
      a single question
- [ ] `docs/architecture.md` reads as one coherent document, not five stitched-together
      phase notes

---

## 7. Working agreement

- This phase fixes seams, it does not redesign layers. If something needs a real
  redesign to integrate properly, stop and tell me — don't quietly rebuild a layer
  while "just fixing the integration."
- Report the Section 3 findings to me before silently fixing anything non-trivial,
  especially anything that touches more than one file across layer boundaries.
- If the review-gate end-to-end check in Section 3.5 fails anywhere in the chain, that
  is the most important bug in the whole project to report clearly — stop and tell me
  exactly where it breaks rather than patching around it.