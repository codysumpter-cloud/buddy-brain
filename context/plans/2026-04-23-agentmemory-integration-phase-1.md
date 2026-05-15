## Problem
The agentmemory repository contains valuable memory crystallization logic that needs to be integrated into the bmo-stack skills to enhance the agent's long-term memory capabilities.

## Smallest useful wedge
Adopt the memory-crystallization skill from agentmemory into bmo-stack/skills/ and ensure it passes validation.

## Verification plan
- Verify that the skill memory-crystallization exists in bmo-stack/skills/ with correct SKILL.md and README.md.
- Run the skill validation script to ensure the skill is correctly registered.
- Test that the skill can be loaded and used without error.
- Check that the cron job for memory crystallization is set up correctly.

## Rollback plan
If any issues arise, remove the skill directory from bmo-stack/skills/ and revert any changes to skills/index.json. The PR can be closed or reverted.

