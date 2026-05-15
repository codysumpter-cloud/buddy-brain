---
name: cron-scheduler
version: 1.0.0
description: |
  Schedule management with staggering, quiet hours, and wake-up override.
  Validates schedules, prevents collisions, and gates delivery during quiet hours.
triggers:
  - "schedule a job"
  - "cron"
  - "quiet hours"
  - "what jobs are running"
tools:
  - search
  - session_search
  - write_file
mutating: true
---

# Cron Scheduler

## Purpose

Provides robust job scheduling capabilities for automating routine tasks in bmo-stack, including schedule validation, collision prevention, and quiet hours handling.

## Problem

Running routine tasks manually is inefficient and error-prone. Without proper scheduling:
- Jobs may collide or overload the system
- Noisy jobs may disturb users during quiet hours
- No tracking of job execution history
- Difficulty in managing and monitoring automated tasks

## Contract

This skill guarantees:

- Schedule staggering: max 1 job per 5-minute slot, no collisions
- Quiet hours gating: timezone-aware, with user-awake override
- Thin job prompts: jobs reference skill files rather than containing inline prompts
- Idempotency: jobs can run twice without duplicate side effects
- Results saved as reports: `logs/cron/{job-name}/{timestamp}.md`

## Phases

1. **Define job.** Name, schedule (cron expression), skill to run, timeout.
2. **Validate schedule.** Check no collision with existing jobs (5-minute offset rule).
   - Slots: :05, :10, :15, :20, :25, :30, :35, :40, :45, :50
   - If collision detected, suggest the next available slot
3. **Check quiet hours.** Default: 11 PM - 8 AM local time.
   - Override: user-awake flag (if user is active, quiet hours suspended)
   - During quiet hours: save output to held queue
   - Morning contact releases the backlog
4. **Register with host scheduler.** Use system cron, launchd, or other available scheduler.
   - Each registered entry should execute via the skill system, not direct agentTurn.
5. **Write thin prompt.** Job prompt is one line: "Run skill {name}".

## Idempotency Requirement

Every cron job MUST be idempotent:
- Running the same job twice produces the same result (no duplicate files, no duplicate state changes)
- Use checkpoint state files to track progress and resume interrupted runs
- Check for existing output before creating new output

## Output Format

Job configuration saved. Report: "Job '{name}' scheduled at {cron expression}. Next run: {time}."

## Anti-Patterns

- Scheduling jobs at the same minute (:00 for everything)
- Inline 3000-word prompts in cron jobs (use skill file references)
- Running cron jobs without testing on 3-5 items first
- Jobs that produce different output on re-run (not idempotent)
- Sending notifications during quiet hours (save to held queue instead)

## Related Files

- `scripts/cron-scheduler/` - implementation scripts
- `logs/cron/` - job execution logs and reports
- `context/skills/SKILLS.md` - for stack-wide cron skills