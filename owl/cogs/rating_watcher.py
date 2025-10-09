import discord
from discord.ext import commands

from owl.embeds import result_embed
from owl.persistence.guild_settings_store import get_settings
from owl.services.rating import rate_message_and_emojis, digit_to_emoji


class RatingWatcher(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return
        s = await get_settings(message.guild.id)
        if not s.judge_channel_id or message.channel.id != s.judge_channel_id:
            return
        if not message.content or not message.content.strip():
            return

        score, emojis = await rate_message_and_emojis(message.content)
        digit = digit_to_emoji(score)
        try:
            if digit:
                await message.add_reaction(digit)
            for e in emojis:
                await message.add_reaction(e)
        except discord.Forbidden:
            pass  # lacking Add Reactions; skip silently

        mini = result_embed("🧮 Owl Rating", f"Score: **{score}** / 9\nEmojis: {' '.join(emojis) if emojis else '—'}")
        await message.channel.send(embed=mini)


async def setup(bot: commands.Bot):
    await bot.add_cog(RatingWatcher(bot))
