#!/usr/bin/env node

import crypto from "node:crypto";
import process from "node:process";

const DEFAULT_ENDPOINT = "http://localhost:2468/event";
const DEFAULT_COMMAND_LIMIT = 120;

function envFlag(name, defaultValue = false) {
  const raw = process.env[name];
  if (raw == null || raw === "") return defaultValue;
  return ["1", "true", "yes", "on"].includes(raw.toLowerCase());
}

function stableSessionId(cwd = process.cwd()) {
  const hash = crypto.createHash("md5").update(cwd).digest("hex").slice(0, 12);
  return `bmo_${hash}`;
}

function isLocalHttpEndpoint(value) {
  try {
    const url = new URL(value);
    return ["http:", "https:"].includes(url.protocol) && ["localhost", "127.0.0.1", "::1"].includes(url.hostname);
  } catch {
    return false;
  }
}

function parsePayload(rawParts) {
  if (rawParts.length === 0) return {};
  const raw = rawParts.join(" ").trim();
  if (!raw) return {};
  try {
    return JSON.parse(raw);
  } catch (error) {
    throw new Error(`Payload must be valid JSON: ${error.message}`);
  }
}

function redactSecrets(value) {
  if (Array.isArray(value)) {
    return value.map(redactSecrets);
  }
  if (value && typeof value === "object") {
    return Object.fromEntries(
      Object.entries(value).map(([key, nested]) => {
        if (/token|secret|password|authorization|cookie|api[_-]?key/i.test(key)) {
          return [key, "[redacted]"];
        }
        return [key, redactSecrets(nested)];
      }),
    );
  }
  if (typeof value === "string") {
    return value
      .replace(/Bearer\s+[A-Za-z0-9._~+/=-]+/gi, "Bearer [redacted]")
      .replace(/sk-[A-Za-z0-9_-]{12,}/g, "sk-[redacted]")
      .replace(/gh[pousr]_[A-Za-z0-9_]{12,}/g, "gh_[redacted]");
  }
  return value;
}

function normalizeEvent(type, payload) {
  const cwd = payload.cwd ?? process.cwd();
  const redactedPayload = redactSecrets(payload);
  const redactPrompts = envFlag("AGENTCRAFT_REDACT_PROMPTS", true);
  const maxCommandChars = Number.parseInt(
    process.env.AGENTCRAFT_MAX_COMMAND_CHARS ?? `${DEFAULT_COMMAND_LIMIT}`,
    10,
  );

  const event = {
    client: process.env.AGENTCRAFT_CLIENT ?? "bmo-stack",
    sessionId: process.env.AGENTCRAFT_SESSION_ID ?? payload.sessionId ?? stableSessionId(cwd),
    cwd,
    type,
    ...redactedPayload,
  };

  if (redactPrompts && typeof event.prompt === "string") {
    event.prompt = "[redacted]";
  }

  if (typeof event.command === "string" && Number.isFinite(maxCommandChars) && maxCommandChars > 0) {
    event.command = event.command.slice(0, maxCommandChars);
  }

  return event;
}

async function postEvent(event) {
  const endpoint = process.env.AGENTCRAFT_EVENT_URL ?? DEFAULT_ENDPOINT;

  if (!isLocalHttpEndpoint(endpoint)) {
    return {
      ok: false,
      skipped: true,
      reason: "AgentCraft endpoint must be local HTTP(S).",
    };
  }

  const response = await fetch(endpoint, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify(event),
    signal: AbortSignal.timeout(Number.parseInt(process.env.AGENTCRAFT_TIMEOUT_MS ?? "750", 10)),
  });

  return { ok: response.ok, status: response.status };
}

async function main() {
  const [type, ...rawPayload] = process.argv.slice(2);
  if (!type) {
    console.error("Usage: agentcraft-report.mjs <event-type> [json-payload]");
    process.exit(2);
  }

  const payload = parsePayload(rawPayload);
  const event = normalizeEvent(type, payload);

  if (!envFlag("AGENTCRAFT_ENABLED", false)) {
    console.log(JSON.stringify({ ok: true, skipped: true, reason: "AGENTCRAFT_ENABLED is not set", event }));
    return;
  }

  try {
    const result = await postEvent(event);
    console.log(JSON.stringify({ ...result, event }));
  } catch (error) {
    // AgentCraft is an optional observability overlay. Never fail the actual runtime path.
    console.log(JSON.stringify({ ok: false, skipped: true, reason: error.message, event }));
  }
}

main().catch((error) => {
  console.error(error.message);
  process.exit(2);
});
