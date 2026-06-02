---
name: prismtek-youtube-buddy-lipsync
description: Produce a Prismtek/Buddy talking-host overlay for narrated videos using pixel-art visemes and FFmpeg audio RMS animation.
version: 1.1.0
author: Prismtek
license: MIT
platforms: [macos, linux]
metadata:
  hermes:
    tags: [youtube, video, ffmpeg, imagemagick, pixel-art, vtuber, buddy, prismtek]
    related_skills: [youtube-content, media-rendering, buddy-appearance]
---

# Prismtek YouTube Buddy Lip-Sync

Use this skill to turn a clean Buddy host PNG into a lightweight audio-reactive talking-host overlay for Prismtek/Buddy videos.

The workflow is intentionally simple and robust:

- no ML lip-sync dependency;
- no face-swap, cloning, impersonation, or deepfake pipeline;
- no private media assets committed;
- ImageMagick for deterministic pixel-art mouth/viseme generation;
- FFmpeg/ffprobe for audio RMS analysis and video compositing;
- JSON receipts for repeatable render review.

## Required Tools

```bash
command -v magick
command -v ffmpeg
command -v ffprobe
python3 --version
```

## Generate Buddy Visemes

```bash
python3 scripts/generate_buddy_v12_visemes.py \
  ~/.hermes/assets/prismtek-youtube/avatar/buddy-host-main-clean.png \
  --out-dir ~/.hermes/assets/prismtek-youtube/avatar
```

## Render a Proof Clip

```bash
python3 scripts/prismtek_youtube_avatar_lipsync.py \
  /path/to/base-video.mp4 \
  --closed ~/.hermes/assets/prismtek-youtube/avatar/buddy-host-main-v12-mouth-closed.png \
  --open ~/.hermes/assets/prismtek-youtube/avatar/buddy-host-main-v12-mouth-small-open.png \
  --output /tmp/buddy-lipsync-proof.mp4 \
  --limit-seconds 20
```

For full render, omit `--limit-seconds`.

## Operator Notes

This skill renders local media only. Keep source media, generated avatars, rendered MP4s, and receipts out of public git history.
