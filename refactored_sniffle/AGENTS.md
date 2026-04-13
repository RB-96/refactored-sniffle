# AGENTS.md - Debate Arena Reference

This file documents the current project for AI coding assistants and contributors.
It describes the actual debate workflow in this repository, not the default CrewAI template.

## Project Summary

This repository implements a multi-agent debate system with:

- a `Pro` debater
- a `Con` debater
- a `Judge`
- a Streamlit interface
- optional web research using Serper

The debate topic comes from the user. The two sides argue, rebut, and the judge
returns a scorecard, winner, and short explanation.

## Current Runtime Shape

- Project type: CrewAI flow
- Primary reusable runner: `run_debate_session()` in `src/refactored_sniffle/main.py`
- UI entrypoint: `src/refactored_sniffle/streamlit_app.py`
- Crew definition: `src/refactored_sniffle/crews/content_crew/content_crew.py`

## Debate Pipeline

The task execution order is:

1. `pro_opening_task` and `con_opening_task` run in parallel
2. `pro_rebuttal_task` runs after the Con opening is available
3. `con_rebuttal_task` runs after the Pro opening is available
4. `judging_task` runs after all four debate outputs are ready

Important:

- The crew still uses `Process.sequential`
- Parallelism is enabled through `async_execution: true` on the two opening tasks
- Do not remove the task contexts on the rebuttal or judge tasks unless intentionally changing debate semantics

## Agents

### Pro Debater

- model source: `OPENAI_MODEL`
- provider: OpenAI
- tools: Serper when `SERPER_API_KEY` is present
- purpose: argue for the motion using research-backed reasoning

### Con Debater

- model source: `OPENAI_MODEL`
- provider: OpenAI
- tools: Serper when `SERPER_API_KEY` is present
- purpose: argue against the motion using research-backed reasoning

### Judge

- model source: `ANTHROPIC_MODEL`
- provider: Anthropic
- purpose: score both sides and declare exactly one winner

## LLM Configuration Pattern

Per-agent model settings are defined in Python with `crewai.LLM` objects inside:

- `_pro_llm()`
- `_con_llm()`
- `_judge_llm()`

This is the preferred place for:

- `temperature`
- `top_p`
- `max_tokens`
- provider/model routing

Do not rely on YAML strings alone when per-agent sampling settings are required.

## Environment Variables

Expected `.env` values:

```env
OPENAI_API_KEY=...
ANTHROPIC_API_KEY=...
SERPER_API_KEY=...
OPENAI_MODEL=openai/gpt-4o-mini
ANTHROPIC_MODEL=anthropic/claude-sonnet-4
```

Also note:

- `CREWAI_STORAGE_DIR` defaults to a local `.crewai` folder in code
- `CREWAI_TRACING_ENABLED` is disabled by default in code

## Files That Matter Most

- `src/refactored_sniffle/main.py`
  - debate state
  - transcript generation
  - winner extraction
  - flow orchestration
- `src/refactored_sniffle/streamlit_app.py`
  - UI layout and user interaction
- `src/refactored_sniffle/crews/content_crew/content_crew.py`
  - agents
  - tools
  - per-agent model setup
- `src/refactored_sniffle/crews/content_crew/config/tasks.yaml`
  - prompts
  - async opening stage
- `src/refactored_sniffle/crews/content_crew/config/agents.yaml`
  - role, goal, and backstory

## Execution Commands

Install and sync dependencies:

```bash
uv sync
```

Run the CrewAI flow:

```bash
uv run crewai run
```

Run the Streamlit app:

```bash
uv run streamlit run src/refactored_sniffle/streamlit_app.py
```

Refresh the lockfile after dependency changes:

```bash
uv lock
uv sync
```

## Editing Guidance

When modifying this project:

- preserve the parallel opening stage unless the debate design is intentionally changing
- keep the judge downstream of all debate outputs
- keep `run_debate_session()` as the shared execution path for both CLI flow and Streamlit UI
- prefer updating prompts in YAML and runtime configuration in Python
- do not remove Serper integration from the debaters unless the product is intentionally moving to a no-research mode

## Common Pitfalls

- Missing `OPENAI_MODEL` or `ANTHROPIC_MODEL` can leave `LLM(model=...)` with invalid values
- Using Anthropic without `ANTHROPIC_API_KEY` will fail at runtime
- Network-restricted environments can block live model calls and Serper lookups
- Updating `pyproject.toml` without `uv lock` can leave the lockfile stale

## Expected User Experience

In Streamlit, the user should be able to:

1. enter a debate topic
2. start the debate
3. see Pro and Con outputs on the page
4. see the judge scorecard and winner
5. download the transcript
