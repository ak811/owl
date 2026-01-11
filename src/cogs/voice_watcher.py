import os
import discord
from discord.ext import commands

from src.embeds import result_embed, error_embed
from src.persistence.guild_settings_store import get_settings
from src.services.transcription import download_file, transcribe_file, cleanup


def is_audio_like(attachment: discord.Attachment) -> bool:
    """
    Consider an attachment transcribable if:
      - Discord marks it as audio/* OR video/*, OR
      - its filename matches a common audio/video extension.
    """
    ct = (attachment.content_type or "").lower()
    if "audio" in ct or "video" in ct:
        return True
    name = (attachment.filename or "").lower()
    exts = (
        ".mp3", ".wav", ".m4a", ".aac", ".ogg", ".oga", ".opus", ".flac", ".wma",
        ".webm", ".mp4", ".m4v", ".mov", ".mkv"
    )
    return any(name.endswith(ext) for ext in exts)


class VoiceWatcher(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return
        s = await get_settings(message.guild.id)
        if not s.voice_channel_id or message.channel.id != s.voice_channel_id:
            return
        if not message.attachments:
            return

        for att in message.attachments:
            if is_audio_like(att):
                temp = f"tmp_{att.filename}"
                try:
                    await download_file(att.url, temp)
                    text = await transcribe_file(temp)
                    if not text.strip():
                        await message.channel.send(embed=error_embed("Transcription failed or empty."))
                        continue
                    chunks = [text[i:i + 1800] for i in range(0, len(text), 1800)]
                    for idx, chunk in enumerate(chunks, 1):
                        title = "📜 Transcription" if len(chunks) == 1 else f"📜 Transcription ({idx}/{len(chunks)})"
                        await message.channel.send(embed=result_embed(title, f"> {chunk}"))
                except Exception:
                    await message.channel.send(embed=error_embed("Couldn't transcribe the audio."))
                finally:
                    cleanup(temp)


async def setup(bot: commands.Bot):
    await bot.add_cog(VoiceWatcher(bot))
