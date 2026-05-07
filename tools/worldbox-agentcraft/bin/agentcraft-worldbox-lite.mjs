#!/usr/bin/env node
import { createServer } from 'node:http';
import { readFileSync, existsSync } from 'node:fs';
import { join } from 'node:path';
import { homedir } from 'node:os';

const stateDir = join(homedir(), '.worldbox-agentcraft');
const logPath = join(stateDir, 'events.jsonl');

function usage() {
  console.log(`agentcraft-worldbox-lite

Tiny local viewer for WorldBox AgentCraft JSONL events.

Usage:
  agentcraft-worldbox-lite help
  agentcraft-worldbox-lite serve [--port 4777]
  agentcraft-worldbox-lite events
`);
}

function readEvents() {
  if (!existsSync(logPath)) return [];
  return readFileSync(logPath, 'utf8')
    .split('\n')
    .filter(Boolean)
    .map((line) => {
      try { return JSON.parse(line); }
      catch { return { type: 'parse_error', raw: line }; }
    });
}

function html(events) {
  const rows = events.slice(-100).reverse().map((e) => `
    <tr>
      <td>${escapeHtml(e.ts || '')}</td>
      <td><code>${escapeHtml(e.type || '')}</code></td>
      <td>${escapeHtml(e.mode || '')}</td>
      <td>${escapeHtml(e.risk || '')}</td>
      <td>${escapeHtml(e.summary || '')}</td>
    </tr>`).join('');
  return `<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <meta http-equiv="refresh" content="2" />
  <title>WorldBox AgentCraft Lite</title>
  <style>
    body { font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, sans-serif; margin: 24px; background: #101418; color: #e9eef5; }
    h1 { margin-bottom: 4px; }
    .muted { color: #91a0af; }
    table { width: 100%; border-collapse: collapse; margin-top: 20px; }
    th, td { border-bottom: 1px solid #2a3440; padding: 8px; text-align: left; vertical-align: top; }
    th { color: #b8c7d8; }
    code { color: #8bd5ff; }
  </style>
</head>
<body>
  <h1>WorldBox AgentCraft Lite</h1>
  <div class="muted">Read-only HUD for ~/.worldbox-agentcraft/events.jsonl. Refreshes every 2s.</div>
  <table>
    <thead><tr><th>Time</th><th>Type</th><th>Mode</th><th>Risk</th><th>Summary</th></tr></thead>
    <tbody>${rows || '<tr><td colspan="5">No events yet.</td></tr>'}</tbody>
  </table>
</body>
</html>`;
}

function escapeHtml(s) {
  return String(s).replace(/[&<>"']/g, (ch) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[ch]));
}

const [cmd, ...rest] = process.argv.slice(2);

switch (cmd) {
  case undefined:
  case 'help':
  case '--help':
  case '-h':
    usage();
    break;

  case 'events':
    console.log(JSON.stringify(readEvents(), null, 2));
    break;

  case 'serve': {
    const idx = rest.indexOf('--port');
    const port = idx >= 0 ? Number(rest[idx + 1]) : 4777;
    const server = createServer((req, res) => {
      if (req.url === '/events') {
        res.writeHead(200, { 'content-type': 'application/json' });
        res.end(JSON.stringify(readEvents(), null, 2));
        return;
      }
      res.writeHead(200, { 'content-type': 'text/html; charset=utf-8' });
      res.end(html(readEvents()));
    });
    server.listen(port, '127.0.0.1', () => {
      console.log(`WorldBox AgentCraft Lite: http://127.0.0.1:${port}`);
    });
    break;
  }

  default:
    console.error(`Unknown command: ${cmd}`);
    usage();
    process.exit(2);
}
