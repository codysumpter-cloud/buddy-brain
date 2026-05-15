# Donor Harvest Matrix & Assimilation Roadmap


## Rollback plan
Revert the PR to remove the harvest matrix.

## Verification plan
Ensure readiness check passes and verify file exists and is properly formatted.

## Smallest useful wedge
Land the HARVEST_MATRIX.md to freeze the capability map.
## Problem
The capability harvest process was manual and undocumented, making it hard to track which donors had which features and the order of assimilation.
This document tracks the systematic assimilation of capabilities from donor forks into the canonical repos.

## Canonical Boundary Mapping
- **bmo-stack**: Contracts, policy, runbooks, integrations, orchestration.
- **prismtek-apps**: Product shell, Buddy UX, feature packs, app surface.
- **omni-bmo**: Runtime, device interface, offline/pairing boundary, MCP core.

## Harvest Matrix

| Donor Repo | Status | Target Repo | Capability to Harvest | Validation Plan | Merge Gate |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `hermes-agent-self-evolution` | Not Started | `bmo-stack` | DSPy/GEPA Optimization Loop | Benchmarking vs baseline skills | 100% Test Pass + Benchmarks |
| `agentic-stack` | Not Started | `bmo-stack` | Portable Brain Structure (`.agent/`) | Cross-harness state transfer test | Integration Test Pass |
| `context-mode` | Not Started | `omni-bmo` | Session Continuity / Sandboxing | Context window usage audit | $\le$ 2% context drift |
| `arcade-mcp` | Not Started | `omni-bmo` | Standardized MCP Auth/Deploy | Server deployment verification | Successful `arcade deploy` |
| `nemoclaw` | Partially | `prismtek-apps` | Specialized shell extensions | Runtime functional audit | Buddy UX Smoke Test |
| `hermes-workspace` | Partially | `prismtek-apps` | Dashboard / API orchestration | API endpoint connectivity test | End-to-end API Green |

## Execution Order
1. **Session Continuity (`context-mode`)** $\rightarrow$ Essential for the stability of all subsequent complex migrations.
2. **Portable Brain (`agentic-stack`)** $\rightarrow$ Establishes the canonical structure for memory/skills.
3. **Self-Evolution (`self-evolution`)** $\rightarrow$ Enables automated improvement of the newly established brain.
4. **MCP Standardization (`arcade-mcp`)** $\rightarrow$ Hardens the tool-calling layer.
5. **Feature Assimilation** $\rightarrow$ All remaining donors.

## Hard Merge Gate Policy
No PR will be merged unless:
- [ ] All required GitHub checks are green.
- [ ] Local validation is verified and documented.
- [ ] No version/build drift is introduced.
- [ ] Lead branch remains 100% green.
