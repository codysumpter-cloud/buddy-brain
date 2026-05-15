---

## Purpose
This skill enables the agent to interact with Model Context Protocol (MCP) servers, allowing it to discover and use external tools and resources through the mcporter CLI.

name: mcp-integration
version: 1.0.0
description: |
  Integrates with Model Context Protocol (MCP) servers. Provides tools to list servers,
  call tools, generate CLI clients, and inspect MCP configurations. Based on mcporter.
triggers:
  - "mcp list"
  - "mcp call"
  - "mcp generate-cli"
  - "mcp inspect"
  - "mcp emit-ts"
tools:
  - terminal
  - file
mutating: true
---
# MCP Integration Skill

This skill provides integration with Model Context Protocol (MCP) servers, leveraging
the mcporter CLI. It enables the agent to discover MCP servers, call their tools,
generate CLI clients, and inspect configurations.

## Contract

- All MCP interactions go through the `mcporter` CLI (must be installed and available in PATH).
- The skill assumes MCP server configurations are available via standard mcporter mechanisms
  (config JSON, editor imports, or ad-hoc flags).
- Tool calls return structured results (text, markdown, or JSON) via the `CallResult` helper.

## Phases

### 1. List MCP Servers
Use `mcporter list` to discover available MCP servers and their tools.

### 2. Call MCP Tools
Use `mcporter call <server>.<tool> <key=value>...` to invoke a tool on an MCP server.

### 3. Generate CLI Clients
Use `mcporter generate-cli --server <name>` to create a standalone CLI for an MCP server.

### 4. Emit TypeScript Definitions
Use `mcporter emit-ts <server> --mode types|client` to generate TypeScript definitions.

### 5. Inspect MCP Binaries
Use `mcporter inspect-cli <path>` to read embedded metadata from a distributed MCP CLI.

## Tool Usage

This skill uses the `terminal` tool to execute `mcporter` commands and the `file` tool
to read/write MCP-related configuration files.

## Example Usage

```bash
# List available MCP servers and tools
mcporter list

# Call a tool on the 'filesystem' server
mcporter call filesystem.read_text path=/tmp/example.txt

# Generate a CLI client for the 'github' server
mcporter generate-cli --server github

# Emit TypeScript types for the 'slack' server
mcporter emit-ts slack --mode types

# Inspect a distributed MCP CLI binary
mcporter inspect-cli ./dist/mcp-server.js
```

## Dependencies

- `mcporter` CLI must be installed and available in the system PATH.
- For full functionality, MCP servers must be configured and accessible.

## Error Handling

- If `mcporter` is not found, the skill will return an error indicating the dependency is missing.
- MCP server connection errors are propagated from the `mcporter` CLI.
- Invalid tool names or arguments will result in MCP protocol errors.

## Notes

This skill wraps the mcporter CLI and does not reimplement MCP logic. It relies on
mcporter for correct MCP protocol handling, including OAuth retries, transport promotion,
and cleanup.