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

Each task record stores provider, model, attempts, model/tool cost, elapsed time, review time, verification, artifact acceptance, rollback state, and security gate. The report calculates completion rate, retry rate, rollback rate, and cost per verified completion.

Model routing should use a meaningful sample and optimize expected cost to an accepted, verified result—not token price in isolation.
