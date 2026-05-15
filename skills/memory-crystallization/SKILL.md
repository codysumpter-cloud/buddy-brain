---
name: memory-crystallization
description: Transforms raw session logs and temporary memories into high-density, structured semantic knowledge.
version: 1.0.0
author: Hermes Agent (Self-Evolved)
tags: [memory, optimization, continuity]
---

## Purpose
This skill was self-evolved from the GitHub fork upgrade process to enhance the agent's capabilities.

# Memory Crystallization

This skill implements the "Crystallization" loop from agentmemory. It prevents context window bloat and memory decay by refining raw data into durable facts.

## The Crystallization Pipeline

1. **Ingestion**: Scan current session logs and `~/.hermes/memory/` for raw, unrefined observations.
2. **Reflection**: Use the internal `reflect` loop to identify recurring patterns, critical technical facts, and user preferences.
3. **Deduplication**: Compare new insights with existing memories to prevent redundant entries.
4. **Crystallization**: Convert a "finding" into a declarative fact.
   - *Raw*: "User mentioned he prefers using the local gemma4 model over cloud because of rate limits."
   - *Crystallized*: "User prefers local gemma4 over cloud due to rate limiting constraints."
5. **Commit**: Save to persistent memory with a timestamp and context tag.

## Execution Workflow

1. **Scan**: Run `session_search` for the last 5 sessions.
2. **Filter**: Extract all "Technical Decisions," "User Preferences," and "Project Architecture" facts.
3. **Refine**: For each fact:
   - Remove conversational filler.
   - Verify against existing memory.
   - Normalize terminology (e.g., "local model" -> "local gemma4").
4. **Persist**: Use `memory(action='add', target='memory', content='...')`.

## Pitfalls
- **Over-Compression**: Losing the "Why" behind a decision. Always preserve the reasoning if it's non-obvious.
- **Stale Truths**: Crystallizing a fact that has since been changed. Always check for contradictions before committing.

## Verification
- Run `memory` list to ensure a concise, non-redundant set of facts.
- Verify that a `session_search` on a specific topic now yields a "Crystallized" result rather than a raw transcript.
