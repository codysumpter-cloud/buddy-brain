#!/usr/bin/env node
import { appendFileSync, mkdirSync, readFileSync, existsSync } from 'node:fs';
import { join } from 'node:path';
import { homedir } from 'node:os';

const stateDir = join(homedir(), '.worldbox-agentcraft');
const logPath = join(stateDir, 'events.jsonl');
const modePath = join(stateDir, 'mode.txt');

function ensureStateDir() {
  mkdirSync(stateDir, { recursive: true });
}

function usage() {
  console.log(`worldboxctl-safe

Safe event/logging CLI for WorldBox + AgentCraft experiments.

This tool intentionally does NOT click WorldBox. It records observations,
proposals, blocks, and mission events while the no-mod input path is untrusted.

Usage:
  worldboxctl-safe help
  worldboxctl-safe mode knowledge|strategist|bridge-research
  worldboxctl-safe status
  worldboxctl-safe mission-start <summary>
  worldboxctl-safe observe <summary>
  worldboxctl-safe propose <summary> [--risk low|medium|high] [--approval]
  worldboxctl-safe block <reason>
  worldboxctl-safe done <summary>
  worldboxctl-safe log-path
  worldboxctl-safe tail [count]

Examples:
  worldboxctl-safe mode knowledge
  worldboxctl-safe mission-start "Build WorldBox Hermes knowledge"
  worldboxctl-safe observe "Laptop closed; command execution paused"
  worldboxctl-safe propose "User manually places ants; agent verifies result" --risk low
  worldboxctl-safe block "Autonomous clicking disabled until mod bridge exists"
`);
}

function parseFlags(args) {
  const out = { risk: 'low', approval: false };
  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--risk') {
      out.risk = args[i + 1] || 'low';
      i++;
    } else if (args[i] === '--approval') {
      out.approval = true;
    }
  }
  return out;
}

function getMode() {
  if (!existsSync(modePath)) return 'knowledge';
  return readFileSync(modePath, 'utf8').trim() || 'knowledge';
}

function emit(type, payload = {}) {
  ensureStateDir();
  const event = {
    ts: new Date().toISOString(),
    source: 'worldboxctl-safe',
    mode: getMode(),
    type,
    ...payload,
  };
  appendFileSync(logPath, JSON.stringify(event) + '\n');
  console.log(JSON.stringify(event, null, 2));
}

const [cmd, ...rest] = process.argv.slice(2);

switch (cmd) {
  case undefined:
  case 'help':
  case '--help':
  case '-h':
    usage();
    break;

  case 'mode': {
    const mode = rest[0];
    const allowed = new Set(['knowledge', 'strategist', 'bridge-research']);
    if (!allowed.has(mode)) {
      console.error('Allowed modes: knowledge, strategist, bridge-research');
      process.exit(2);
    }
    ensureStateDir();
    appendFileSync(modePath, mode + '\n');
    emit('mode_changed', { mode });
    break;
  }

  case 'status': {
    ensureStateDir();
    console.log(JSON.stringify({
      ok: true,
      mode: getMode(),
      logPath,
      autonomousGameplayClicking: false,
      reason: 'No-mod WorldBox input is untrusted. Use manual human actions or mod bridge.',
    }, null, 2));
    break;
  }

  case 'mission-start':
    emit('mission_start', { summary: rest.join(' ') || 'WorldBox mission started', risk: 'low' });
    break;

  case 'observe':
    emit('game_observation', { summary: rest.join(' ') || 'Observation recorded', risk: 'low' });
    break;

  case 'propose': {
    const flags = parseFlags(rest);
    const summary = rest.filter((x, i, arr) => x !== '--risk' && arr[i - 1] !== '--risk' && x !== '--approval').join(' ');
    emit('game_action_proposed', {
      summary: summary || 'Action proposed',
      risk: flags.risk,
      requiresApproval: flags.approval || flags.risk !== 'low',
    });
    break;
  }

  case 'block':
    emit('game_action_blocked', { summary: rest.join(' ') || 'Action blocked', risk: 'medium', requiresApproval: true });
    break;

  case 'done':
    emit('mission_done', { summary: rest.join(' ') || 'Mission completed', risk: 'low' });
    break;

  case 'log-path':
    ensureStateDir();
    console.log(logPath);
    break;

  case 'tail': {
    ensureStateDir();
    const count = Number(rest[0] || 20);
    if (!existsSync(logPath)) {
      console.log('(no events yet)');
      break;
    }
    const lines = readFileSync(logPath, 'utf8').trim().split('\n').filter(Boolean);
    console.log(lines.slice(-count).join('\n'));
    break;
  }

  default:
    console.error(`Unknown command: ${cmd}`);
    usage();
    process.exit(2);
}
