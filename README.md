# Owl (Discord Bot)

A Discord bot that keeps your server mildly more functional than it deserves: **definitions**, **pronunciation (TTS)**, **auto-translation**, **audio transcription**, **message “coolness” ratings**, and **quick GPT replies when mentioned**.

Built with `discord.py` and OpenAI.

---

## What it does

### Core features
- **Dictionary mode**
  - Post a word/phrase in a configured “dictionary channel” and Owl replies with quick meanings, synonyms/antonyms, and examples.
- **Definitions (commands)**
  - `!owl def` for a quick definition
  - `!owl deff` for a fuller multi-sense definition
- **Pronunciation (TTS)**
  - Generates an MP3 for the requested text with accent support.
- **Translation watcher**
  - In a configured channel, Owl detects language and replies with an English translation.
- **Voice transcription watcher**
  - In a configured channel, Owl downloads audio/video attachments and transcribes them with Whisper.
- **Judge / rating watcher**
  - In a configured channel, Owl rates messages (0–9) and reacts with emoji.
- **GPT mentions**
  - Mention the bot for a short reply.
  - Add a `-` anywhere in the message to enable short “memory mode” using recent channel history.

---

## Commands

Prefix: `!`

### Help
- `!owl`  
  Shows the built-in command list.

### Dictionary / definitions
- `!owl def <word or phrase>`  
  Quick, single-meaning definition.
- `!owl deff <word or phrase>`  
  Full definition with multiple meanings and extras.

### Pronunciation
- `!owl p [accent] <text>`
- `!owl pronounce [accent] <text>`

Accents supported:
- `us` (default), `uk`, `au`, `in`, `ca`, `ie`, `za`

Examples:
- `!owl p hello`
- `!owl p uk schedule`
- `!owl p au no worries mate`

### Server settings (Manage Server permission required)
- `!owl set translation-channel #channel` or `!owl set translation-channel off`
- `!owl set transcription-channel #channel` or `!owl set transcription-channel off`
  - `!owl set voice-channel ...` is also supported as an alias.
- `!owl set judge-channel #channel` or `!owl set judge-channel off`
- `!owl set dictionary-channel #channel` or `!owl set dictionary-channel off`
- `!owl settings`  
  Shows current guild settings.

---

## Setup

### 1) Requirements
- Python **3.11+**
- A Discord bot token
- An OpenAI API key

Install system dependencies as needed for audio handling (varies by OS). Whisper can work without `ffmpeg` for some formats, but having `ffmpeg` installed makes transcription far less painful.

### 2) Install
From the repository root:

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
# optionally, if you have packaging configured:
pip install -e .
```

### 3) Configure environment variables
Copy the example file and fill it in:

```bash
cp .env.example .env
```

**.env**
```bash
DISCORD_TOKEN="your_discord_token"
OPENAI_API_KEY="your_openai_api_key"

# Optional overrides
FASTTEXT_MODEL_PATH="models/lid.176.bin"
WHISPER_DEVICE="cpu"   # or "cuda" if you know what you're doing
```

### 4) Run the bot
```bash
python run.py
```

On first run, Owl initializes a SQLite database at:
- `data/owl.sqlite3`

---

## How the watchers work

Owl uses server settings stored per guild to decide where to listen:
- **Translation watcher:** listens only in the configured translation channel.
- **Transcription watcher:** listens only in the configured transcription channel; transcribes audio/video attachments.
- **Rating watcher:** listens only in the configured judge channel; reacts + posts a small embed.
- **Dictionary watcher:** listens only in the configured dictionary channel; treats each message as a lookup query.
- **GPT mentions:** responds to mentions in *other* channels (it avoids the watcher channels).

---

## Data storage

- SQLite via `aiosqlite`
- Table: `guild_settings`
  - `guild_id` (primary key)
  - `translation_channel_id`
  - `voice_channel_id` (used for transcription channel)
  - `judge_channel_id`
  - `dictionary_channel_id`
  - `updated_at`

The bot will auto-migrate and add missing columns on startup.

---

## Language detection (fastText)

This repo uses fastText language identification (`lid.176.bin`). If the model file is missing, the bot will attempt to download it automatically from Meta’s public hosting.

You can also download it manually and set:
- `FASTTEXT_MODEL_PATH=models/lid.176.bin`

---

## Transcription (Whisper)

Transcription uses the Python `whisper` package and loads the `"base"` model by default.

Performance notes:
- CPU works, but it’s slower.
- Setting `WHISPER_DEVICE=cuda` can speed it up if you have a compatible GPU and the right PyTorch setup.

---

## Discord permissions & intents

The bot enables these intents (see `src/config.py`):
- `guilds`
- `emojis`
- `voice_states`
- `message_content`
- `messages`
- `reactions`

You must also enable **Message Content Intent** in your bot’s Discord Developer Portal settings for the watchers and commands to work reliably.

The bot may need these permissions in channels where you use it:
- Read messages / View channel
- Send messages
- Embed links
- Attach files (for MP3 pronunciation)
- Add reactions (for judge mode)

---

## License

MIT. See `LICENSE`.
