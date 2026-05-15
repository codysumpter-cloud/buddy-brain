# memory.md

## 2026-05-13 current agent direction

OpenClaw is retired for current work. Hermes-agent is the current main working agent system. Buddy-agent is being prepared to become the primary and eventually only agent repository. KnowledgeVault / Obsidian remains the source of truth for project memory and handoffs.

Relay preference: PrismBot / Discord-safe outputs should be <=1,500 characters, no code fences, no markdown tables, no emoji, no backticks, no line breaks, and compressed relay-safe wording.

See [[99-System/Memory/2026-05-13-prismtek-agent-direction-and-memory-import]] for the full saved/inferred memory import.

## Hermes Mac handoff — 2026-05-13

Created a Mac-safe Hermes handoff and performance policy. Hermes should use low-priority, once-daily, non-overlapping maintenance only; no watchers, all-repo clones, heavy indexing, Docker/npm/Xcode builds, model downloads, or OpenClaw work by default.