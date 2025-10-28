# Owl 🦉 Discord Bot

Prefix-command bot with embeds-only responses.

## Features
- `!owl p [accent] [words]` — Pronunciation (default accent: `us`)
- `!owl def [word]` — Quick definition
- `!owl deff [word]` — Full definition
- `!owl set translation-channel [#channel|off]`
- `!owl set transcription-channel [#channel|off]` _(alias: `voice-channel`)_
- `!owl set judge-channel [#channel|off]`
- `!owl settings` — Show guild settings
- Auto-translate in translation channel
- Auto-transcribe audio/video in transcription channel
- Rating + emoji reactions in judge channel
- Mention `@Owl` for quick replies; add `-` for memory mode

## Setup
1. Copy `.env.example` → `.env` and fill values.
2. Install:
   ```bash
   pip install -e .
