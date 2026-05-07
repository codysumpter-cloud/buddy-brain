#!/usr/bin/env node

function usage() {
  console.log(`worldboxmod-plan

Planning helper for the real WorldBox mod bridge. This tool does not install mods,
modify WorldBox, or run untrusted code.

Usage:
  worldboxmod-plan help
  worldboxmod-plan roadmap
  worldboxmod-plan checklist
  worldboxmod-plan nml-brief
  worldboxmod-plan agent-policy
`);
}

const ROADMAP = `# WorldBox Mod Bridge Roadmap

1. Stop autonomous no-mod clicking.
   - Screen viewer remains useful for observation.
   - User performs manual clicks when needed.

2. Prefer NML/NeoModLoader for the bridge path.
   - BepInEx remains a secondary route.
   - NCMS is legacy research only.

3. Implement read-only bridge first.
   - GET /ping
   - GET /status
   - GET /observe
   - GET /selected

4. Map local WorldBox assemblies/classes.
   - actors
   - kingdoms
   - cities
   - cultures
   - religions
   - wars
   - traits
   - powers/actions

5. Add proposal-only AI Director.
   - AI proposes actions.
   - BMO/AgentCraft records risk and approvals.
   - Nothing destructive runs directly.

6. Add allowlisted safe writes.
   - pause/resume
   - speed
   - inspect/select
   - spawn harmless creatures in test zones
   - apply safe powers only after proof

7. Gate dangerous writes.
   - dragons, plague, meteors, city destruction, wars
   - require explicit human approval
   - log before and after state
`;

const CHECKLIST = `# Read-only Bridge Checklist

- [ ] Identify installed WorldBox path.
- [ ] Confirm desktop build, not mobile.
- [ ] Install preferred mod loader manually.
- [ ] Create minimal bridge mod.
- [ ] Bind localhost only.
- [ ] Add session token.
- [ ] Implement /ping.
- [ ] Implement /status.
- [ ] Implement /observe with world summary.
- [ ] Confirm no arbitrary C# eval.
- [ ] Confirm no shell execution from the mod.
- [ ] Confirm no file writes outside bridge config/logs.
- [ ] Emit AgentCraft events for observation and blocked actions.
- [ ] Do not add write actions until read-only is verified.
`;

const NML = `# NML Bridge Brief

Use NML/NeoModLoader as the preferred route because current community docs point away from NCMS.

Bridge principles:

- Localhost only: 127.0.0.1.
- Token required for every command.
- Read-only endpoints first.
- Allowlisted commands only.
- No eval.
- No remote shell.
- No arbitrary file access.
- Structured JSON protocol shared with worldboxctl.
- Dangerous commands require BMO/AgentCraft approval.

Target endpoints:

GET  /ping
GET  /status
GET  /observe
GET  /selected
POST /command
GET  /events

Do not claim the mod is complete until it has been compiled against local WorldBox assemblies and tested in-game.
`;

const POLICY = `# Agent Policy

Until the mod bridge exists and passes read-only tests:

- Do not click WorldBox autonomously.
- Do not use synthetic input for achievement attempts.
- Do not start new maps.
- Do not place creatures.
- Do not spam Escape.
- Do not clear UI blindly.
- Use screen viewing only for observation.
- Ask Prismtek for manual actions when needed.
- Emit observations/proposals/blocks through worldboxctl-safe.
- Work on Hermes knowledge and bridge research.

Allowed modes:

1. knowledge
   - research, summarize, build runbooks
2. strategist
   - guide the user through manual steps
3. bridge-research
   - plan and scaffold the real mod bridge
`;

const [cmd] = process.argv.slice(2);

switch (cmd) {
  case undefined:
  case 'help':
  case '--help':
  case '-h':
    usage();
    break;
  case 'roadmap':
    console.log(ROADMAP);
    break;
  case 'checklist':
    console.log(CHECKLIST);
    break;
  case 'nml-brief':
    console.log(NML);
    break;
  case 'agent-policy':
    console.log(POLICY);
    break;
  default:
    console.error(`Unknown command: ${cmd}`);
    usage();
    process.exit(2);
}
