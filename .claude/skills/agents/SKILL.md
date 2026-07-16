---
name: agents
description: Guidelines and instructions for the Agents Layer.
---

# Agents Layer Guidelines

When working on the Agents Layer for TerraPulse, strictly adhere to the following rules:

1. **Sequential Pipeline**: Unstructured text is processed via a 3-step pipeline (Extract -> Score -> Fuse).
2. **Model Provider**: Do NOT use proprietary/paid APIs like Anthropic. Use an OpenAI-compatible SDK defaulting to OpenRouter/Groq with `meta-llama/llama-3-8b-instruct:free`. This avoids lock-in and paid API key dependencies.
3. **Strict Typed Contracts**: Each LLM step must output JSON matching Pydantic schemas. Use `response_format={"type": "json_object"}`.
4. **Review Gate Rule (CRITICAL)**: In the final Fuse step, compare the agent's qualitative livability signal against structured metrics using hardcoded logic. If there is a disagreement, you MUST flag the summary for human review by setting `needs_human_review = True`.
