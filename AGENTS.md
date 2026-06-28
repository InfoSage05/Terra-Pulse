# AGENTS.md — Phase 2: Agent Layer

This file extends the original AGENTS.md. Ingestion and Storage are now complete:
Postgres + PostGIS is running, migrations 001-006 are applied, `areas` is seeded, and
the PPR, OSM, CSO, and crime connectors run end-to-end with dead-letter handling.

**This phase builds ONLY the Agent Layer.** Do not touch `ingestion/` or `storage/`
except to read from them. Do not start on `models_layer/`, `backend/`, or `frontend/`.

---

## 1. What the agent layer is for

Some signals about an area cannot be captured by structured data alone — local context,
recent news, planning/development chatter, qualitative "what is this area like" framing.
The agent layer's job is to turn unstructured text (scraped articles, council notices,
planning applications) into a small set of structured, validated outputs that get stored
alongside the structured metrics from Phase 1, and eventually surface in the API and
frontend as a "neighbourhood summary."

**Important constraint, decided deliberately:** this is a sequential pipeline of agents
with strict typed contracts between steps — not a multi-agent swarm with autonomous
delegation. Benchmarking from Princeton NLP found a single well-scoped agent matches or
beats multi-agent setups on most tasks when given equivalent tools and context, and each
extra agent hop adds real latency and token cost for no accuracy gain. Do not build a
planner/supervisor agent that dynamically spawns sub-agents. Build exactly the three
steps below, in order, every time.

---

## 2. The three-step pipeline

```
raw text (per area)  →  [1] EXTRACT  →  [2] SCORE/SUMMARISE  →  [3] FUSE + REVIEW GATE  →  storage
```

### Step 1 — Extract
- Input: raw scraped text for one area (news article, council notice, etc.) plus the
  area_id it belongs to.
- Output: a structured Pydantic object — NOT free text. Fields: `topics` (list of enum
  values: e.g. `development`, `crime_incident`, `amenity_change`, `transport_change`,
  `general`), `key_facts` (list of short strings, max ~15 words each, no verbatim long
  quotes from the source), `sentiment` (enum: positive/neutral/negative/mixed),
  `mentioned_entities` (list of strings — place names, project names).
- The LLM call must be instructed to return ONLY JSON matching this schema. Validate the
  response against the Pydantic model immediately. If it fails validation, retry once
  with an error message appended to the prompt telling the model what was wrong. If it
  fails twice, log to `data/dead_letter/agent_extract/` and skip this record — do not
  crash the pipeline and do not pass invalid data downstream.

### Step 2 — Score / Summarise
- Input: the validated output of Step 1, for one area, potentially aggregated across
  multiple source texts collected for that area in this run.
- Output: a structured Pydantic object with: `area_id`, `summary` (2-3 sentences, plain
  English, written fresh — not copied from source text), `livability_signal`
  (float -1.0 to 1.0, where the agent's qualitative read of the area's trajectory is
  encoded numerically), `confidence` (float 0-1, how much source material backed this),
  `flags` (list of enum: e.g. `low_source_count`, `conflicting_signals`,
  `recent_negative_news`).
- Same validation/retry/dead-letter rule as Step 1.
- If `confidence` is below a configurable threshold (default 0.3), set `flags` to
  include `low_source_count` and still return a result — do not fabricate confidence.

### Step 3 — Fuse + Review Gate
- Input: Step 2's output for an area, PLUS the structured metrics already in Postgres
  for that same area (price trend, crime_stats counts, demographics).
- Logic here is NOT an LLM call — this step is deterministic code, not another agent.
  Compare the agent's `livability_signal` direction against what the structured data
  would suggest (e.g. if crime_stats counts have risen sharply but the agent's signal is
  strongly positive, or vice versa). This is a simple rule-based check, not another
  model call.
- Output: the final `area_agent_summary` record (see schema in Section 3), with an added
  `needs_human_review` boolean. Set it `true` when the agent's qualitative signal and
  the structured data disagree beyond a configurable threshold, or when `confidence` was
  low. This flag is the actual production-grade behaviour we want here: the system
  should know when to distrust itself, not silently average away a contradiction.
- Do NOT auto-resolve disagreements by picking one side. Store both signals plus the
  flag, so a human (or, later, a more careful process) can inspect it.

---

## 3. Storage additions (new migration, do not modify existing tables)

Add ONE new migration file: `storage/migrations/007_agent_summaries.sql`

```sql
CREATE TABLE area_agent_summaries (
    id SERIAL PRIMARY KEY,
    area_id INTEGER REFERENCES areas(id),
    run_id UUID NOT NULL,                  -- groups all summaries from one pipeline run
    summary TEXT NOT NULL,
    livability_signal FLOAT NOT NULL,       -- -1.0 to 1.0
    confidence FLOAT NOT NULL,              -- 0 to 1
    flags JSONB,                             -- list of flag strings
    needs_human_review BOOLEAN NOT NULL DEFAULT FALSE,
    structured_data_snapshot JSONB,          -- the metrics compared against, for audit
    source_count INTEGER NOT NULL,
    model_name TEXT NOT NULL,                -- e.g. "claude-sonnet-4-6" — always log which model produced this
    source_name TEXT NOT NULL DEFAULT 'agent_pipeline',
    ingested_at TIMESTAMP NOT NULL DEFAULT now()
);
CREATE INDEX idx_agent_summaries_area ON area_agent_summaries(area_id);
CREATE INDEX idx_agent_summaries_review ON area_agent_summaries(needs_human_review);
```

Adjust column types if they conflict with existing conventions in migrations 001-006 —
match whatever pattern those files already use for FKs, timestamps, and JSON columns.

---

## 4. Codebase structure for this phase

```
agents_layer/
├── schemas/
│   ├── extraction_result.py     # Pydantic model for Step 1 output
│   ├── score_result.py          # Pydantic model for Step 2 output
│   └── fused_summary.py         # Pydantic model for Step 3 output (matches migration 007)
├── steps/
│   ├── extract.py               # Step 1: LLM call + validation + retry + dead-letter
│   ├── score.py                 # Step 2: LLM call + validation + retry + dead-letter
│   └── fuse.py                  # Step 3: deterministic comparison logic, NO LLM call
├── llm_client.py                  # thin wrapper around the Anthropic API client —
│                                   #   one place that handles the API call, retries on
│                                   #   transient errors, and enforces JSON-only output
├── pipeline.py                    # orchestrates extract -> score -> fuse for one area
├── jobs/
│   └── run_agent_pipeline.py      # CLI entrypoint: run pipeline for one area, all
│                                   #   areas, or areas with text collected since a date
├── text_sources/
│   └── council_news_connector.py  # pulls raw text per area for the agents to process —
│                                   #   this is the ONE new ingestion-adjacent piece this
│                                   #   phase needs; reuses the base connector pattern
│                                   #   from ingestion/connectors/base.py, do not duplicate it
└── tests/
    ├── fixtures/                   # sample raw text + expected structured outputs
    ├── test_extract.py
    ├── test_score.py
    └── test_fuse.py               # test the deterministic logic with constructed
                                     #   disagreement cases — this is the part most worth
                                     #   testing since it has no LLM randomness
```

---

## 5. Design rules specific to this layer

- **JSON-only LLM calls.** Every prompt to the model must explicitly state "respond with
  ONLY valid JSON matching this schema, no preamble, no markdown fences." Strip any
  accidental ```` ```json ```` fences defensively before parsing anyway.
- **One model call per step, no internal chaining inside a step.** Step 1 makes exactly
  one LLM call per input text (plus up to 1 retry). Step 2 makes exactly one LLM call per
  area per run (plus up to 1 retry). Do not let an agent decide to call itself again or
  call other tools — these are plain prompt-in, JSON-out calls.
- **Always log `model_name` and a `run_id`** with every output, so any summary in the
  database can be traced back to exactly what model and run produced it. This matters
  if the model is swapped or upgraded later.
- **Cost awareness.** Batch text per area before calling Step 1 where possible rather
  than one call per sentence/paragraph. Log token usage per run to the console summary.
- **No tool use inside the LLM calls in this phase.** Do not give the model web search,
  code execution, or other tools yet — these are closed-form text-in, JSON-out
  transformations. Keep this phase simple and deterministic to test; tool-using agents
  are a later iteration once this baseline is proven reliable.
- **Reuse, don't duplicate.** The Step 1-3 validation/retry/dead-letter pattern should
  closely mirror the connector pattern already built in `ingestion/connectors/base.py`.
  If that base class is generic enough, consider extending it rather than writing
  parallel logic — ask me first if you think this requires changing the base class,
  since that touches Phase 1 code.

---

## 6. What "done" looks like for this phase

- [ ] Migration `007_agent_summaries.sql` applies cleanly on top of the existing schema
- [ ] `council_news_connector.py` pulls real raw text for at least 3 seeded areas (websites for council/news scraping should reuse the same source-vetting approach in SOURCES.md before this is "real" — confirm sources with me before scraping)
- [ ] Running `run_agent_pipeline.py --area-id <id>` produces one row in
      `area_agent_summaries` for that area, with a sensible summary, a `confidence`
      score, and `needs_human_review` set correctly when I manually construct a
      contradictory test case
- [ ] Invalid/unparseable LLM responses are retried once, then dead-lettered, and do not
      crash the run
- [ ] Console output after a run shows: areas processed, summaries created, summaries
      flagged for review, approximate token usage
- [ ] `docs/architecture.md` is updated with a short section describing this pipeline
- [ ] At least one test in `test_fuse.py` proves the review-gate logic actually catches
      a constructed disagreement between agent signal and structured data

---

## 7. Working agreement (same as Phase 1, repeated for emphasis)

- Confirm with me before choosing which real text sources to scrape for
  `council_news_connector.py` — do not silently pick sources.
- Ask before changing anything in `ingestion/` or `storage/migrations/001-006`.
- If the existing `areas`/`property_sales`/etc. schema from Phase 1 differs from what's
  assumed here, stop and tell me the actual column names so this phase's foreign keys
  and JOINs are correct — do not guess and proceed.