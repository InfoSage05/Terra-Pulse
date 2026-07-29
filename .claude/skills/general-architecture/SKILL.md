---
name: general-architecture
description: General architecture rules and directives for TerraPulse.
---

# TerraPulse General Architecture Rules

You are an AI assistant working on the TerraPulse platform. This system is a rigid, unidirectional pipeline composed of five distinct layers.

## Core Directives
1. **Pipeline Integrity**: Ensure data flows sequentially from Ingestion -> Agents -> Models -> Backend -> Frontend.
2. **CRITICAL: needs_human_review Flag**: This boolean flag originates in the Agents Layer when qualitative data disagrees with structured metrics. It MUST traverse unchanged through the DB, Backend API, and finally appear as an unmissable warning in the Frontend UI. Never drop or silence this flag.
3. **Open-Source LLMs**: The system uses OpenRouter/Groq with `meta-llama/llama-3-8b-instruct:free`. Do not introduce paid proprietary LLM dependencies.
4. **Strict Schemas**: Use Pydantic schemas for data validation across boundaries.

## Known Infrastructure Problems to Fix ASAP
- **Postgres & Redis not running**: Ports 5432 and 6379 are closed. Nothing can be persisted or cached. We must start them via Docker.
- **Python venv is broken**: `.venv/bin/pip` is missing, no deps installed. Needs to be recreated so connectors can import dependencies.
- **No automated migration runner**: SQL DDL exists (`storage/migrations/`) but must be applied manually. We need an automated migration runner.
