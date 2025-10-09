import os
from dotenv import load_dotenv
import discord

BOT_PREFIX = "!"
OWL_INTENTS = discord.Intents(
    guilds=True,
    members=False,
    bans=False,
    emojis=True,
    integrations=False,
    webhooks=False,
    invites=False,
    voice_states=True,
    presences=False,
    message_content=True,
    messages=True,
    reactions=True,
    typing=False,
)

DISCORD_TOKEN = ""
OPENAI_API_KEY = ""
FASTTEXT_MODEL_PATH = os.getenv("FASTTEXT_MODEL_PATH", "models/lid.176.bin")
WHISPER_DEVICE = os.getenv("WHISPER_DEVICE", "cpu")

def load_env():
    load_dotenv(override=False)
    global DISCORD_TOKEN, OPENAI_API_KEY
    DISCORD_TOKEN = os.getenv("DISCORD_TOKEN", "").strip()
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
    if not DISCORD_TOKEN:
        raise RuntimeError("DISCORD_TOKEN is missing. Put it in .env")
    if not OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY is missing. Put it in .env")
