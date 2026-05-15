---
name: buddy-evolve
description: Allows the Buddy to mutate its own operational kernel to improve performance.
trigger: "evolve kernel" or "upgrade buddy logic"
---

# Buddy Evolve

## Purpose
To implement self-recursive evolution by mutating the `BUDDY_KERNEL.md` based on performance audits.

## Process
1. **Audit**: Analyze the recent conversation history and tool outputs for friction points.
2. **Identify**: Locate the specific section of the `BUDDY_KERNEL.md` that governs the failing behavior.
3. **Propose**: Define a `Mutation` consisting of `oldText` $\rightarrow$ `newText`.
4. **Execute**: Call the `EvolutionEngine` to apply the change.
5. **Log**: Record the mutation in `evolution.log` with the supporting reasoning.

## Safety Guards
- **No Destructive Changes**: Do not remove "Core Identity" or "Operational Invariants".
- **Incrementalism**: Only mutate one section at a time.
- **Human Oversight**: All mutations must be presented to the user for approval before final commit.
