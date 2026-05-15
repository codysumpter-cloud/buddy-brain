---

## Purpose
This skill was self-evolved from the GitHub fork upgrade process to enhance the agent's capabilities.

name: tool-failure-diagnostic
description: Autonomous reflexive diagnostic loop triggered upon tool execution failure.
version: 1.0.0
author: Hermes Agent (Self-Evolved)
tags: [reliability, debugging, autonomy]
---

# Tool Failure Diagnostic Reflex

This skill transforms a failure from a "stop" event into a "diagnostic" event. Instead of reporting an error, the agent enters a specialized recovery mode.

## The Diagnostic Loop

1. **Symptom Capture**: Extract the exact `stderr` and `exit_code`.
2. **Context Audit**: 
   - Check current working directory (`pwd`).
   - Verify dependency existence (e.g., if a command like `gh` failed, check if it's installed).
   - Check filesystem permissions for the targeted path.
3. **Hypothesis Generation**: Use internal reasoning to determine if the failure is:
   - **Transient**: Network fluke, API 500.
   - **Configuration**: Missing env var, incorrect path.
   - **Logic**: Bug in the command arguments.
4. **Corrective Action**:
   - If Transient $ightarrow$ Retry with exponential backoff.
   - If Configuration $ightarrow$ Run `doctor` scripts or update `.env`.
   - If Logic $ightarrow$ Use `read_file` to inspect the target and propose a patch.
5. **Verification**: Re-run the original command to confirm the fix.

## Integration
This logic should be called immediately when a `terminal` or `execute_code` tool returns an exit code != 0.
