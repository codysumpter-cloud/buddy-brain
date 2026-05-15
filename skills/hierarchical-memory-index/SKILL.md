---

## Purpose
This skill was self-evolved from the GitHub fork upgrade process to enhance the agent's capabilities.

name: hierarchical-memory-index
description: Implements a multi-tier memory system (Immediate -> Short-Term -> Long-Term/Crystallized) to optimize recall and minimize context bloat.
version: 1.0.0
author: Hermes Agent (S-E)
tags: [memory, lcm, architecture]
---

# Hierarchical Memory Indexing (LCM Implementation)

This skill replaces linear memory files with a three-tier retrieval system inspired by the `hermes-lcm` architecture.

## The Memory Tier System

1. **L1: Working Memory (Context Window)**
   - Current session state, immediate goals.
   - *Action*: Managed via `TASK_STATE.md` and active context.

2. **L2: Short-Term Semantic Cache (Daily/Weekly Notes)**
   - High-fidelity logs of recent events.
   - *Action*: Managed via `memory/YYYY-MM-DD.md`.

3. **L3: Long-Term Crystallized Core (Global Truths)**
   - De-duplicated, validated facts.
   - *Action*: Managed via `memory.md` and `USER.md`.

## The Indexing Loop

- **Promotion**: When a fact in L2 is referenced 3+ times across different sessions -> Promote to L3 (Crystallize).
- **Demotion/Eviction**: When L2 notes exceed a size threshold -> Summarize into L3 and archive raw log.
- **Cross-Reference**: Every L3 fact should link back to the L2 session date that generated it for provenance.

## Execution Workflow

1. **Audit**: Scan L2 files for recurring patterns.
2. **Synthesize**: Use the `memory-crystallization` skill to create a durable fact.
3. **Index**: Map the fact to a specific "Domain" (e.g., #architecture, #user-pref, #bmo-stack).
4. **Verify**: Ensure no contradictions exist between the new L3 fact and existing truths.

## Verification
- Run `session_search` using a domain tag (e.g., "search #architecture") and verify the result is a distilled L3 fact.
