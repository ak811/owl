from dataclasses import dataclass
from typing import Optional

@dataclass
class GuildSettings:
    guild_id: int
    translation_channel_id: Optional[int] = None
    voice_channel_id: Optional[int] = None
    judge_channel_id: Optional[int] = None
    dictionary_channel_id: Optional[int] = None
