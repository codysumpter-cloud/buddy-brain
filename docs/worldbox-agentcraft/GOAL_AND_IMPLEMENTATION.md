# WorldBox AgentCraft Goal and Implementation

## Product goal

Turn the WorldBox screen-control experiment into a safe AgentCraft orchestration prototype.

The goal is not just to make an agent click WorldBox. The goal is to build a command-room model where AI agents can observe, propose, coordinate, and eventually control simulation actors through explicit policy gates.

## Roles

- **Prismtek**: human commander and approval authority.
- **BMO runtime**: safety, receipts, policy, and durable state.
- **AgentCraft HUD**: observability surface for missions, risks, and agent state.
- **WorldBox**: live sandbox and testbed.
- **Screen viewer**: perception layer only.
- **worldboxctl-safe**: safe event/logging wrapper.
- **worldboxmod-plan**: bridge planning helper.
- **Future NML/BepInEx bridge**: real game-state API.

## Current decision

The no-mod autonomous click path is not trusted on the current machine. The agent may observe and guide, but must not claim it can autonomously start maps, place creatures, or farm achievements through pixels.

## Implementation path

1. Knowledge and strategist mode now.
2. Use `worldboxctl-safe` to log observations, proposals, blocked actions, and completed steps.
3. Use `agentcraft-worldbox-lite` as a local HUD for the JSONL event stream.
4. Use `worldboxmod-plan` for read-only bridge planning.
5. Build the real NML/BepInEx bridge locally against the installed WorldBox assemblies.
6. Implement read-only endpoints first.
7. Add allowlisted safe writes after read-only is verified.
8. Gate dangerous actions with explicit BMO/AgentCraft approval.

## Safe current workflow

```text
screen viewer observes WorldBox
agent records observation
agent proposes manual user action
user acts with real mouse
agent verifies by screen viewer
agent emits AgentCraft event
```

## Future workflow

```text
WorldBox mod bridge observes game state
AI Director proposes high-level actions
BMO/AgentCraft classifies risk and approval needs
safe allowlisted command is executed
bridge reports result
HUD shows mission progress
```

## Non-goals

- No arbitrary C# execution.
- No remote shell from a game mod.
- No unlogged destructive actions.
- No pixel-click autonomy until proven by diagnostics.
- No pretending a skeleton mod is a working game API.
