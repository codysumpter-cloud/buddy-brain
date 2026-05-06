# Buddy Symphony Integration

## What Symphony adds for Buddies

Symphony turns issue-tracker work into repeatable, isolated implementation runs. For Buddies, that means BMO can stop treating coding-agent work as one-off manual sessions and start treating it as a supervised queue of Buddy missions.

The key value is not that Symphony replaces Buddy runtime. It does not. The key value is that Symphony gives Buddies a reliable work loop:

1. Find eligible work.
2. Claim one item.
3. Create or reuse an isolated workspace.
4. Run the coding agent inside that workspace.
5. Collect proofs.
6. Hand the result back for BMO review.
7. Retry, cancel, or release work based on policy.

## Correct architecture

```text
Issue tracker / local queue
  -> Symphony scheduler-runner
  -> isolated workspace
  -> coding-agent run
  -> proofs and summaries
  -> BMO receipt conversion
  -> Buddy runtime event stream
  -> Buddy state machine
  -> BeMore Mission Control
```

## What not to do

Do not let Symphony directly mutate Buddy state. Symphony should not directly award XP, promote memory, evolve Buddies, publish packages, or claim source changes landed. BMO must convert Symphony outputs into receipts and runtime events first.

## Buddy mission lifecycle

```text
queued
  -> claimed
  -> preparing
  -> running
  -> waiting_review
  -> accepted
```

Failure and rejection paths:

```text
running -> failed
running -> canceled
waiting_review -> rejected
```

## Proof requirements

A Buddy Symphony run needs proof before it can affect Buddy state.

Useful proof kinds:

- `diff`: reviewable source diff
- `pr`: pull request reference
- `ci_status`: validation result
- `review_feedback`: code review or council feedback
- `complexity`: rough complexity/risk readout
- `walkthrough`: demonstration or summary video reference
- `artifact`: generated file or build output
- `receipt`: BMO receipt proving a durable action

## Buddy growth rule

Symphony may recommend growth. BMO applies growth.

A run may recommend Buddy proficiency growth only after:

1. A known Buddy owns the work item.
2. The run has at least one proof.
3. The proof has been converted into a BMO receipt.
4. Council or operator review accepts the run.
5. The Buddy state machine allows the effect.

## Generated workflow

Use this script to create a Buddy-safe Symphony workflow template:

```bash
node scripts/generate-buddy-symphony-workflow.mjs --output WORKFLOW.buddy.md
```

Customize the Linear project slug and workspace root when needed:

```bash
node scripts/generate-buddy-symphony-workflow.mjs \
  --project-slug "$LINEAR_PROJECT_SLUG" \
  --workspace-root "./.buddy-symphony/workspaces" \
  --output WORKFLOW.buddy.md
```

Print without writing:

```bash
node scripts/generate-buddy-symphony-workflow.mjs --print
```

Overwrite intentionally:

```bash
node scripts/generate-buddy-symphony-workflow.mjs --force --output WORKFLOW.buddy.md
```

## Recommended local checks

```bash
node scripts/generate-buddy-symphony-workflow.mjs --print > /tmp/WORKFLOW.buddy.md
node scripts/generate-buddy-symphony-workflow.mjs --output /tmp/WORKFLOW.buddy.md --force
make runtime-doctor
```

## Future BeMore surface

The app should render Buddy Symphony as read-only Mission Control first:

- active Buddy missions
- run state
- workspace/status summaries
- pending approvals
- proofs collected
- final handoff summary

The app should not execute Symphony directly from iOS. Use Mac/runtime relay for approved execution paths.
