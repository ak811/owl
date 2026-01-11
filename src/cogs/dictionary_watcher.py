import discord
from discord.ext import commands

from src.persistence.guild_settings_store import get_settings
from src.services.definitions import fetch_glossary
from src.services.translation import clean_mentions  # reuse mention cleaning

class DictionaryWatcher(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return
        s = await get_settings(message.guild.id)
        if not s.dictionary_channel_id or message.channel.id != s.dictionary_channel_id:
            return

        text = clean_mentions(message.content or "")
        text = text.strip().strip("`").strip("*").strip("_")
        if not text:
            return

        # Keep it simple: use the entire message as the query term/phrase.
        embed = await fetch_glossary(text)
        await message.channel.send(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(DictionaryWatcher(bot))
