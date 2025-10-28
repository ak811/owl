import asyncio
import logging
import sys

import discord
from discord.ext import commands

from owl.config import BOT_PREFIX, load_env, OWL_INTENTS
from owl.logging_config import setup_logging
from owl.persistence.db import init_db


async def main():
    load_env()
    setup_logging()

    bot = commands.Bot(command_prefix=BOT_PREFIX, intents=OWL_INTENTS, help_command=None)

    # Load cogs
    for ext in [
        "owl.cogs.owl_commands",
        "owl.cogs.translation_watcher",
        "owl.cogs.voice_watcher",
        "owl.cogs.rating_watcher",
        "owl.cogs.gpt_mentions",
        "owl.cogs.dictionary_watcher",
    ]:
        try:
            await bot.load_extension(ext)
            logging.getLogger("owl").info(f"Loaded cog: {ext}")
        except Exception as e:
            logging.getLogger("owl").exception(f"Failed to load {ext}: {e}")

    @bot.event
    async def on_ready():
        logging.getLogger("owl").info(f"Logged in as {bot.user} (ID: {bot.user.id})")
        await init_db()

    from owl.config import DISCORD_TOKEN
    await bot.start(DISCORD_TOKEN)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Shutting down…")
        sys.exit(0)
