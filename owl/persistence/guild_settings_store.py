from typing import Optional

from .db import get_db
from owl.models.guild_settings import GuildSettings

async def get_settings(guild_id: int) -> GuildSettings:
    async with get_db() as db:
        async with db.execute(
            "SELECT guild_id, translation_channel_id, voice_channel_id, judge_channel_id, dictionary_channel_id "
            "FROM guild_settings WHERE guild_id = ?",
            (guild_id,),
        ) as cur:
            row = await cur.fetchone()
            if not row:
                return GuildSettings(guild_id)
            return GuildSettings(
                guild_id=row[0],
                translation_channel_id=row[1],
                voice_channel_id=row[2],
                judge_channel_id=row[3],
                dictionary_channel_id=row[4],
            )

async def upsert_settings(
    guild_id: int,
    translation_channel_id: Optional[int] = None,
    voice_channel_id: Optional[int] = None,
    judge_channel_id: Optional[int] = None,
    dictionary_channel_id: Optional[int] = None,
) -> GuildSettings:
    existing = await get_settings(guild_id)
    if translation_channel_id is not None:
        existing.translation_channel_id = translation_channel_id
    if voice_channel_id is not None:
        existing.voice_channel_id = voice_channel_id
    if judge_channel_id is not None:
        existing.judge_channel_id = judge_channel_id
    if dictionary_channel_id is not None:
        existing.dictionary_channel_id = dictionary_channel_id

    async with get_db() as db:
        await db.execute(
            """
            INSERT INTO guild_settings (guild_id, translation_channel_id, voice_channel_id, judge_channel_id, dictionary_channel_id)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(guild_id) DO UPDATE SET
              translation_channel_id=excluded.translation_channel_id,
              voice_channel_id=excluded.voice_channel_id,
              judge_channel_id=excluded.judge_channel_id,
              dictionary_channel_id=excluded.dictionary_channel_id,
              updated_at=datetime('now')
            """,
            (
                existing.guild_id,
                existing.translation_channel_id,
                existing.voice_channel_id,
                existing.judge_channel_id,
                existing.dictionary_channel_id,
            ),
        )
        await db.commit()
    return existing

async def clear_channel(guild_id: int, which: str) -> GuildSettings:
    settings = await get_settings(guild_id)
    if which == "translation":
        settings.translation_channel_id = None
    elif which == "voice":
        settings.voice_channel_id = None
    elif which == "judge":
        settings.judge_channel_id = None
    elif which == "dictionary":
        settings.dictionary_channel_id = None

    return await upsert_settings(
        guild_id,
        translation_channel_id=settings.translation_channel_id,
        voice_channel_id=settings.voice_channel_id,
        judge_channel_id=settings.judge_channel_id,
        dictionary_channel_id=settings.dictionary_channel_id,
    )
