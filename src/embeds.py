import discord
from typing import Iterable, Optional, Tuple

OWL_COLOR_INFO = discord.Color.blue()
OWL_COLOR_SUCCESS = discord.Color.teal()
OWL_COLOR_WARN = discord.Color.gold()
OWL_COLOR_ERROR = discord.Color.red()

def base_embed(title: str | None = None, desc: str | None = None, color=OWL_COLOR_INFO) -> discord.Embed:
    e = discord.Embed(color=color)
    if title:
        e.title = title
    if desc:
        e.description = desc
    return e

def info_embed(title: str, desc: str | None = None) -> discord.Embed:
    return base_embed(title, desc, OWL_COLOR_INFO)

def success_embed(title: str, fields: Optional[Iterable[Tuple[str, str, bool]]] = None) -> discord.Embed:
    e = base_embed(title, color=OWL_COLOR_SUCCESS)
    if fields:
        for name, value, inline in fields:
            e.add_field(name=name, value=value, inline=inline)
    return e

def error_embed(title: str, hint: str | None = None) -> discord.Embed:
    return base_embed(f"⚠️ {title}", hint or "Please try again.", OWL_COLOR_ERROR)

def result_embed(title: str, body: str, footer: Optional[str] = None) -> discord.Embed:
    e = base_embed(title, body, OWL_COLOR_INFO)
    if footer:
        e.set_footer(text=footer)
    return e

def settings_embed(guild_name: str, translation_ch: str, voice_ch: str, judge_ch: str, dictionary_ch: str) -> discord.Embed:
    e = base_embed(f"🛠️ Owl Settings — {guild_name}", color=OWL_COLOR_SUCCESS)
    e.add_field(name="Translation Channel", value=translation_ch or "—", inline=False)
    e.add_field(name="Transcription Channel", value=voice_ch or "—", inline=False)
    e.add_field(name="Judge Channel", value=judge_ch or "—", inline=False)
    e.add_field(name="Dictionary Channel", value=dictionary_ch or "—", inline=False)
    return e
