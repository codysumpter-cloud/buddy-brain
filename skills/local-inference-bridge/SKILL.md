---

## Purpose
This skill was self-evolved from the GitHub fork upgrade process to enhance the agent's capabilities.

name: local-inference-bridge
description: Routes complex reasoning and heavy-lifting prompts to the local Ollama instance to maximize local GPU/CPU utilization and bypass cloud rate limits.
version: 1.0.0
author: Hermes Agent (Local-First)
tags: [performance, local-llm, gpu-optimization]
---

# Local Inference Bridge

This skill allows the agent to leverage the host's local GPU/CPU by executing prompts via the Ollama CLI.

## The Local Routing Loop

1. **Evaluation**: If a task is "heavy" (e.g., analyzing 10+ files, rewriting a large module, or deep architectural reasoning), trigger local routing.
2. **Dispatch**: Use `terminal(command='ollama run <model> "<prompt>"')`.
3. **Ingestion**: Capture the stdout of the local model.
4. **Synthesis**: Use the cloud brain (if available) only for final formatting or high-level orchestration, while keeping the "heavy lifting" local.

## When to use Local routing
- **Deep Code Reviews**: Analyzing logic across multiple files.
- **Large Scale Refactoring**: Generating large blocks of code.
- **Privacy-Sensitive Work**: When data should not leave the local machine.
- **Rate-Limit Avoidance**: When the cloud provider is unstable or slow.

## Verification
- Run `ollama list` to verify the model is present.
- Test with a simple `ollama run <model> "Hello from the bridge"` call.
