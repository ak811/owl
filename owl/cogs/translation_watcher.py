import discord
from discord.ext import commands

from owl.embeds import result_embed
from owl.persistence.guild_settings_store import get_settings
from owl.services.translation import detect_language, translate_to_english, get_flag, clean_mentions


class TranslationWatcher(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return
        s = await get_settings(message.guild.id)
        if not s.translation_channel_id or message.channel.id != s.translation_channel_id:
            return

        cleaned = clean_mentions(message.content)
        if not cleaned.strip():
            return

        lang, conf = detect_language(cleaned)
        translated = await translate_to_english(cleaned)
        src_flag = get_flag(lang)
        dst_flag = get_flag("en")
        e = result_embed("🌐 Translation",
                         f"{src_flag} → {dst_flag}\n\n> {translated}",
                         footer=f"Requested by {message.author.display_name} • Confidence {conf:.2f}")
        await message.channel.send(embed=e)


async def setup(bot: commands.Bot):
    await bot.add_cog(TranslationWatcher(bot))
