# Media Skill Bundle

## Purpose

`skills/media/` groups operator-side media workflow references that are not yet promoted into standalone top-level runtime skills.

Use this bundle for safe, local-only media production references such as Buddy avatar visemes, talking-host overlays, render receipts, and FFmpeg/ImageMagick command notes.

## Source of truth

- `skills/media/prismtek-youtube-buddy-lipsync/SKILL.md`
- `skills/media/prismtek-youtube-buddy-lipsync/skill.manifest.json`

## Safety posture

Media workflows in this directory are local reference workflows unless their scripts, tests, and runtime dependencies are committed and validated.

Do not commit private source media, generated avatars, rendered MP4s, receipts containing sensitive paths, credentials, tokens, or user-specific raw assets.

## Default action

`status` — review the available media workflow references and confirm whether a given workflow is runnable, documentation-only, or blocked on missing local assets/tools.
