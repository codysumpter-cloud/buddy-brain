# Prismtek Buddy Stack

Buddy Brain is the **governance and measurement layer** of the Prismtek Buddy Agent Platform. It does not retrieve private data directly and it does not perform guarded runtime actions.

Its machine-readable ownership and dependencies are declared in [`prismtek.component.json`](prismtek.component.json). The canonical topology is maintained by BUAP.

## Buddy Brain owns

- council and operator policy
- repository readiness scoring
- routing feedback
- trust-policy outcome reporting
- cost per verified completion

## Trust Fabric reporting

Buddy Agent produces policy decisions, verification receipts, and task economics. Buddy Brain aggregates those records without treating retrieval success as completion.

```bash
python scripts/buddy_trust_fabric_report.py build/run-a build/run-b \
  --format markdown \
  --output build/trust-fabric-report.md
```

The report separates allow, review, and block decisions; stale and conflicting evidence; verified artifact completion; direct cost; and human review time.
