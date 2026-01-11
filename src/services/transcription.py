import asyncio
import os
from typing import Optional

import aiohttp
import whisper

from src.config import WHISPER_DEVICE

_TRANSCRIBER: Optional[whisper.Whisper] = None

async def _get_transcriber():
    global _TRANSCRIBER
    if _TRANSCRIBER is None:
        _TRANSCRIBER = await asyncio.to_thread(whisper.load_model, "base", device=WHISPER_DEVICE)
    return _TRANSCRIBER

async def download_file(url: str, save_path: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            resp.raise_for_status()
            with open(save_path, "wb") as f:
                f.write(await resp.read())

async def transcribe_file(path: str) -> str:
    model = await _get_transcriber()
    result = await asyncio.to_thread(model.transcribe, path)
    return result.get("text", "")

def cleanup(path: str):
    try:
        if os.path.exists(path):
            os.remove(path)
    except Exception:
        pass
