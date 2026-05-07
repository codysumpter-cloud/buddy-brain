#!/usr/bin/env node

import fs from "node:fs";
import path from "node:path";
import process from "node:process";

const DEFAULT_OUTPUT = "WORKFLOW.buddy.md";

function parseArgs(argv) {
  const args = { output: DEFAULT_OUTPUT, projectSlug: "$LINEAR_PROJECT_SLUG", workspaceRoot: "./.buddy-symphony/workspaces" };
  for (let index = 0; index < argv.length; index += 1) {
    const arg = argv[index];
    if (arg === "--output" || arg === "-o") {
      args.output = argv[++index];
    } else if (arg === "--project-slug") {
      args.projectSlug = argv[++index];
    } else if (arg === "--workspace-root") {
      args.workspaceRoot = argv[++index];
    } else if (arg === "--force") {
      args.force = true;
    } else if (arg === "--print") {
      args.print = true;
    } else if (arg === "--help" || arg === "-h") {
      args.help = true;
    } else {
      throw new Error(`Unknown argument: ${arg}`);
    }
  }
  return args;
}

function renderWorkflow({ projectSlug, workspaceRoot }) {
  return `---
tracker:
  kind: linear
  api_key: "$LINEAR_API_KEY"
  project_slug: "${projectSlug}"
  active_states:
    - Todo
    - In Progress
  terminal_states:
    - Done
    - Canceled
    - Cancelled
    - Duplicate
polling:
  interval_ms: 30000
workspace:
  root: "${workspaceRoot}"
hooks:
  timeout_ms: 60000
agent:
  max_concurrent_agents: 3
  max_turns: 8
  max_retry_backoff_ms: 300000
codex:
  command: "codex app-server"
  turn_timeout_ms: 3600000
  read_timeout_ms: 5000
  stall_timeout_ms: 300000
buddy:
  contract: contracts/buddy_symphony.md
  runtime_contract: contracts/buddy_runtime.md
  event_catalog: buddy-runtime-events.v1.json
  state_machine: buddy-state-machine.v1.json
  receipts_required: true
  direct_growth_effects_allowed: false
---
You are running a Buddy Symphony implementation task for BMO.

Issue:
- Identifier: {{ issue.identifier }}
- Title: {{ issue.title }}
- State: {{ issue.state }}
- Priority: {{ issue.priority }}
- URL: {{ issue.url }}
- Labels: {{ issue.labels | join: ", " }}

Description:
{{ issue.description }}

Attempt:
{{ attempt }}

Buddy operating rules:

1. Treat Symphony as a scheduler and isolated work runner only.
2. Do not mutate Buddy state, XP, bond, memory, unlocks, or evolution directly.
3. Any source mutation must produce a reviewable diff or PR reference.
4. Any persistence claim must include a receipt reference.
5. Any memory promotion must include evidence.
6. Any risky or destructive action must request approval before proceeding.
7. Keep all commands inside the assigned workspace.
8. Prefer small, testable changes with clear validation notes.
9. When blocked, produce a precise handoff summary instead of pretending success.

Expected output:

- Summary of changes attempted.
- Files changed or proposed.
- Validation commands run and results.
- Diff, PR, artifact, or receipt references.
- Buddy growth recommendation, if any, as a recommendation only.
- Explicit blockers and next step if not complete.
`;
}

function printHelp() {
  console.log(`Usage: generate-buddy-symphony-workflow.mjs [options]

Options:
  -o, --output <path>          Output workflow path. Default: ${DEFAULT_OUTPUT}
      --project-slug <slug>    Linear project slug or env reference. Default: $LINEAR_PROJECT_SLUG
      --workspace-root <path>  Symphony workspace root. Default: ./.buddy-symphony/workspaces
      --print                  Print to stdout instead of writing a file.
      --force                  Overwrite an existing output file.
  -h, --help                   Show this help.
`);
}

function main() {
  const args = parseArgs(process.argv.slice(2));
  if (args.help) {
    printHelp();
    return;
  }

  const workflow = renderWorkflow(args);

  if (args.print) {
    process.stdout.write(workflow);
    return;
  }

  const outputPath = path.resolve(args.output);
  if (fs.existsSync(outputPath) && !args.force) {
    throw new Error(`${args.output} already exists. Use --force to overwrite.`);
  }

  fs.mkdirSync(path.dirname(outputPath), { recursive: true });
  fs.writeFileSync(outputPath, workflow, "utf8");
  console.log(`Wrote ${args.output}`);
}

try {
  main();
} catch (error) {
  console.error(error.message);
  process.exit(1);
}
