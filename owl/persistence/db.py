import aiosqlite
import logging

_DB_PATH = "owl.sqlite3"

async def get_db():
    return await aiosqlite.connect(_DB_PATH)

async def init_db():
    async with aiosqlite.connect(_DB_PATH) as db:
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS guild_settings (
                guild_id INTEGER PRIMARY KEY,
                translation_channel_id INTEGER NULL,
                voice_channel_id INTEGER NULL,
                judge_channel_id INTEGER NULL,
                updated_at TEXT DEFAULT (datetime('now'))
            )
            """
        )
        await db.commit()
    logging.getLogger("owl.db").info("Database initialized")
