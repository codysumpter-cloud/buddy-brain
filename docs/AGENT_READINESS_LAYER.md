# Buddy Agent Readiness Layer

This layer measures whether a repository can support guarded agent work and whether a provider/model reaches accepted results efficiently.

## Repository readiness

```bash
python3 scripts/buddy_agent_readiness.py /path/to/repo
python3 scripts/buddy_agent_readiness.py /path/to/repo --metrics agent-metrics.json --format json
```

The score intentionally weights evidence instead of raw agent activity:

- instruction coverage;
- deterministic setup;
- automated tests;
- browser verification where applicable;
- security gates;
- agent pull-request acceptance;
- review rework.

A high PR count without merges, verification, and low regression/rework does not improve readiness.

## Cost to verified completion

```bash
python3 scripts/buddy_task_economics.py task-records.jsonl
python3 scripts/buddy_task_economics.py task-records.jsonl --human-hour-rate 100 --format json
```

Each task record stores provider, model, attempts, model/tool cost, elapsed time, review time, verification, artifact acceptance, rollback state, and security gate. Records may also include a `harness_identity` object:

```json
{
  "harness": "buddy-agent",
  "effort": "medium",
  "buap_artifact_hash": "abc123",
  "runtime_adapter_version": "local-container-v1",
  "memory_strategy": "knowledge-vault-public-safe",
  "context_strategy": "compact",
  "reasoning_retention": true,
  "tool_policy_version": "policy-v1"
}
```

The report calculates completion rate, retry rate, rollback rate, and cost per verified completion. Provider/model results are grouped by the complete harness fingerprint, preventing records with different prompts, adapters, memory, compaction, reasoning retention, or tool policy from being averaged together. Legacy records remain readable but are marked as incomplete harness evidence.

Model routing should use a meaningful sample and optimize expected cost to an accepted, verified result—not token price in isolation.

## Model lifecycle registry

`config/model-registry.json` is Buddy's routing authority. Provider catalogs and newly enabled models do not become approved automatically. The default status is `quarantined`.

```bash
python3 scripts/buddy_model_registry.py config/model-registry.json
python3 scripts/buddy_model_registry.py config/model-registry.json \
  --check-route provider/model bounded_edit
```

The lifecycle is:

```text
discovered -> quarantined -> benchmarked -> security_reviewed -> supervised -> approved -> deprecated
```

The implementation enforces evidence-bearing transitions rather than treating the sequence as documentation only. Security-reviewed, supervised, and approved states require an attributable reviewer. Approved models require explicit task classes. Supervised models are denied unless the caller opts into supervised routing, and any approved model can be immediately re-quarantined when behavior changes.

Provider/model discovery should add metadata under quarantine. Benchmark, security, supervised-run, approval, and deprecation evidence should be durable references rather than raw prompts, credentials, or private conversation content.
