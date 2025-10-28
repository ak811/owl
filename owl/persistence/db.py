import aiosqlite
import logging

_DB_PATH = "owl.sqlite3"

def get_db():
    # Return the connection context manager (unawaited)
    return aiosqlite.connect(_DB_PATH)

async def _ensure_column(db, table: str, column: str, ddl: str):
    # Add column if it doesn't exist
    async with db.execute(f"PRAGMA table_info({table})") as cur:
        cols = [row[1] async for row in cur]
    if column not in cols:
        await db.execute(f"ALTER TABLE {table} ADD COLUMN {column} {ddl}")

async def init_db():
    async with get_db() as db:
        # base table
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
        # migrations
        await _ensure_column(db, "guild_settings", "dictionary_channel_id", "INTEGER NULL")
        await db.commit()
    logging.getLogger("owl.db").info("Database initialized")
