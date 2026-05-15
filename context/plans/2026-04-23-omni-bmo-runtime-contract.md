## Problem
The bmo-stack repository needs to adopt the canonical Omni-BMO runtime contract and related schemas to ensure compatibility with the omni-bmo runtime implementation and downstream products.

## Smallest useful wedge
Add the Omni-BMO runtime contract mirror, transport and runtime profile schemas, and the remote operator mode runbook to bmo-stack.

## Verification plan
- Verify that the files `docs/runtime/OMNI_BMO_RUNTIME_CONTRACT.md`, `schemas/transport-state.schema.json`, `schemas/runtime-profile.schema.json`, and `docs/runbooks/OMNI_BMO_REMOTE_OPERATOR_MODE.md` exist and have been added.
- Check that the content matches the expected mirrors from the omni-bmo repository.
- Ensure that any existing tests or validation scripts pass.

## Rollback plan
If any issues arise, remove the added files and revert any changes to the repository. The PR can be closed or reverted.
