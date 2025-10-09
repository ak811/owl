import re
import discord
from discord.ext import commands

from owl.embeds import result_embed
from owl.persistence.guild_settings_store import get_settings
from owl.services.gpt_utils import get_client

TOKEN_LIMIT = 200
OWL_NAME = "Owl 🦉"

def remove_mentions(text: str) -> str:
    text = re.sub(r"<@!?[0-9]+>", "", text)
    return text.strip()

class GptMentions(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def _is_excluded_channel(self, guild, channel_id: int) -> bool:
        s = await get_settings(guild.id)
        excluded = {s.translation_channel_id, s.voice_channel_id, s.judge_channel_id}
        return channel_id in excluded

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return
        if not (message.mentions and any(user.id == self.bot.user.id for user in message.mentions)):
            return
        if await self._is_excluded_channel(message.guild, message.channel.id):
            return

        cleaned = remove_mentions(message.content)
        use_memory = "-" in cleaned

        history = []
        if use_memory:
            async for msg in message.channel.history(limit=50, before=message.created_at):
                if msg.author.bot:
                    role = "assistant" if msg.author == self.bot.user else "user"
                else:
                    role = "user"
                if msg.content:
                    history.append({"role": role, "content": f"{msg.author.display_name}: {msg.content.strip()}"})
            history = list(reversed(history))[-20:]  # keep it short

        system_prompt = (
            "You are Owl 🦉, a witty but thoughtful assistant in a Discord server. "
            "Be helpful, kind, and sharp. Keep replies under 200 tokens."
        ) if use_memory else (
            "You are Owl 🦉, a smart assistant in a Discord server. "
            f"Keep it short, lighthearted, and clever. Under {TOKEN_LIMIT} tokens."
        )

        payload = [{"role": "system", "content": system_prompt}]
        payload.extend(history)
        payload.append({"role": "user", "content": cleaned})

        client = get_client()
        res = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=payload,
            max_tokens=TOKEN_LIMIT,
        )
        reply = res.choices[0].message.content.strip()
        await message.channel.send(embed=result_embed(f"🦉 {OWL_NAME} says", reply))


async def setup(bot: commands.Bot):
    await bot.add_cog(GptMentions(bot))
