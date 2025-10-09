import discord
from discord.ext import commands

from owl.embeds import info_embed, success_embed, error_embed, settings_embed
from owl.services.definitions import fetch_definition
from owl.services.pronunciation import build_tts, cleanup_file, ACCENT_MAP
from owl.persistence.guild_settings_store import get_settings, upsert_settings, clear_channel


class OwlCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.group(name="owl", invoke_without_command=True)
    async def owl_group(self, ctx: commands.Context):
        e = info_embed("🦉 Owl Commands",
            "`!owl` — Show this help\n"
            "`!owl def [word]` — Quick definition\n"
            "`!owl deff [word]` — Full definition\n"
            "`!owl p [accent] [words]` — Pronounce\n"
            "`!owl set translation-channel [#channel|off]`\n"
            "`!owl set voice-channel [#channel|off]`\n"
            "`!owl set judge-channel [#channel|off]`\n"
            "`!owl settings` — Show current server settings"
        )
        await ctx.send(embed=e)

    @owl_group.command(name="def")
    async def owl_def(self, ctx: commands.Context, *, word: str):
        embed = await fetch_definition(word, full=False)
        await ctx.send(embed=embed)

    @owl_group.command(name="deff")
    async def owl_deff(self, ctx: commands.Context, *, word: str):
        embed = await fetch_definition(word, full=True)
        await ctx.send(embed=embed)

    @owl_group.command(name="p", aliases=["pronounce"])
    async def owl_pronounce(self, ctx: commands.Context, accent: str = "us", *, words: str | None = None):
        if words is None:
            words, accent = accent, "us"
        accent = accent.lower()
        if accent not in ACCENT_MAP:
            words = f"{accent} {words}".strip()
            accent = "us"
        try:
            path = build_tts(words, accent)
            e = success_embed("🔊 Pronunciation", fields=[
                ("Word", words, True),
                ("Accent", accent, True),
            ])
            await ctx.send(embed=e, file=discord.File(path, filename=path))
        except Exception:
            await ctx.send(embed=error_embed("Couldn't generate pronunciation."))
        finally:
            cleanup_file(path if "path" in locals() else "")

    # ---------------- Settings ----------------
    @owl_group.group(name="set")
    @commands.has_permissions(manage_guild=True)
    async def owl_set(self, ctx: commands.Context):
        if ctx.invoked_subcommand is None:
            await ctx.send(embed=info_embed("Usage", "`!owl set translation-channel #channel|off` etc."))

    @owl_set.command(name="translation-channel")
    @commands.has_permissions(manage_guild=True)
    async def set_translation(self, ctx: commands.Context, channel: discord.TextChannel | str):
        guild_id = ctx.guild.id
        if isinstance(channel, str) and channel.lower() == "off":
            s = await clear_channel(guild_id, "translation")
            await ctx.send(embed=success_embed("Translation channel cleared."))
            return
        s = await upsert_settings(guild_id, translation_channel_id=channel.id)
        await ctx.send(embed=success_embed("✅ Translation channel set.", fields=[("Channel", channel.mention, True)]))

    @owl_set.command(name="voice-channel")
    @commands.has_permissions(manage_guild=True)
    async def set_voice(self, ctx: commands.Context, channel: discord.TextChannel | str):
        guild_id = ctx.guild.id
        if isinstance(channel, str) and channel.lower() == "off":
            await clear_channel(guild_id, "voice")
            await ctx.send(embed=success_embed("Voice/transcription channel cleared."))
            return
        s = await upsert_settings(guild_id, voice_channel_id=channel.id)
        await ctx.send(embed=success_embed("✅ Voice/transcription channel set.", fields=[("Channel", channel.mention, True)]))

    @owl_set.command(name="judge-channel")
    @commands.has_permissions(manage_guild=True)
    async def set_judge(self, ctx: commands.Context, channel: discord.TextChannel | str):
        guild_id = ctx.guild.id
        if isinstance(channel, str) and channel.lower() == "off":
            await clear_channel(guild_id, "judge")
            await ctx.send(embed=success_embed("Judge channel cleared."))
            return
        s = await upsert_settings(guild_id, judge_channel_id=channel.id)
        await ctx.send(embed=success_embed("✅ Judge channel set.", fields=[("Channel", channel.mention, True)]))

    @owl_group.command(name="settings")
    async def show_settings(self, ctx: commands.Context):
        s = await get_settings(ctx.guild.id)
        def fmt(cid): return ctx.guild.get_channel(cid).mention if cid and ctx.guild.get_channel(cid) else "—"
        e = settings_embed(
            ctx.guild.name,
            fmt(s.translation_channel_id),
            fmt(s.voice_channel_id),
            fmt(s.judge_channel_id)
        )
        await ctx.send(embed=e)


async def setup(bot: commands.Bot):
    await bot.add_cog(OwlCommands(bot))
