# 2026-04-23 – Slice 1: AgentMemory Integration

This document outlines the first phase of adopting the **agentmemory** repository across the key projects.

## Objectives

1. **Hermes runtime on the Mac:** install and configure agentmemory as the persistent memory back –end for the local `hermes-agent` installation.
2. **Runtime/operator truth in `bmo-stack`:** wire agentmemory into the existing runtime contracts so that Buddy and council actions can access and write durable memories.
3. **Buddy experience in `prismtek-apps`:** expose memory features in the product shell so that users can see and influence what Buddy remembers.

## Scope and deliverables

### Hermes runtime (Mac)

- Add `agentmemory` as a Python dependency in the `hermes-agent` project, ideally pinning a stable release.
- Configure a local memory store (for example, an SQLite or file –based store) and connect it to the existing memory loop used by Hermes.
- Register agentmemory’s retrieval and write functions as Hermès tools/skills so that user queries can access their stored memories.
- Provide an opt –in path to migrate existing memory files or notes into the agentmemory store.

### `bmo-stack`

- Import `agentmemory` as a dependency for runtime modules that handle memory (e.g. council seat state, routines, and skill context).
- Define an interface/contract layer so that council actions (via the MCP or runtime glue) can read and write memories through agentmemory.
- Update existing routines (such as `memory-grooming`) to use agentmemory for summarization, archiving, and retrieval instead of manual file manipulations.
- Document the memory API in `context/skills/SKILLS.md` and ensure the contract is reflected in machine –readable manifests.

### `prismtek-apps`

- Add API endpoints or GraphQL resolvers to invoke memory retrieval and storage via the runtime (`bmo-stack`) adapter.
- Expose UI components that allow the user to view remembered facts (e.g. past preferences, project notes) and to clear or amend them.
- Ensure that any product –facing memory surfaces honour user privacy and opt –out requirements (e.g. no implicit memory logging without user consent).
- Keep Buddy personalization surfaces (appearance, performance, animation) separate from memory retrieval, but allow memory to inform default behaviors.

## Workflow

1. **Research integration points**. Review `agentmemory`’s API and examples to understand how to instantiate a memory store and perform CRUD operations.
2. **Prototype locally** on the Mac by adding agentmemory to a clone of `hermes-agent` and writing a small tool that reads/writes data.
3. **Draft contracts** for `bmo-stack` (e.g. TypeScript interfaces or JSON schemas) that describe how memory entries are passed between the runtime and the agent.
4. **Add endpoints** in `prismtek-apps` to fetch and mutate memory via the runtime; wire them into existing Buddy services.
5. **Iterate in small phases**, merging each minimal change and verifying that it does not regress existing behaviours.

## Risks and mitigations

- **Breaking existing storage**: if `hermes-agent` currently reads/writes plain files for memory, introduce agentmemory in parallel and migrate gradually.
- **Privacy and data minimization**: ensure the memory store only contains data the user explicitly wants to persist; provide clear controls to inspect and delete memories.
- **Runtime version drift**: pin consistent versions of agentmemory across all repos and document the upgrade path.

## Next steps

1. Pull and review the `agentmemory` repository to understand its public API.
2. Create minimal PRs in each repository to add agentmemory as a dependency and provide a basic wrapper class or service.
3. Write tests or scripts to validate read/write operations through the new memory layer.
4. Update documentation (`README.md`, `SKILLS.md`, etc.) to include memory usage instructions and developer setup.
