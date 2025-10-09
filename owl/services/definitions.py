import aiohttp
from typing import Tuple, Any
from owl.embeds import result_embed, error_embed, base_embed

DICTIONARY_URL = "https://api.dictionaryapi.dev/api/v2/entries/en/{}"

def _build_full_embed(data: Any, word: str):
    e = base_embed(f"🔍 Definition of **{word}**")
    entry = data[0]
    phonetics = entry.get("phonetics", [])
    phonetics_text = "\n".join([p.get("text", "") for p in phonetics if p.get("text")])
    if phonetics_text:
        e.add_field(name="Phonetics", value=phonetics_text[:1024], inline=False)

    meanings = entry.get("meanings", [])
    for meaning in meanings:
        pos = meaning.get("partOfSpeech", "—")
        defs = meaning.get("definitions", [])
        buf = []
        for idx, d in enumerate(defs, start=1):
            line = f"**{idx}.** {d.get('definition', '')}"
            ex = d.get("example")
            if ex:
                line += f"\n*Example:* {ex}"
            buf.append(line)
            if len("\n".join(buf)) > 900:
                buf.append("…")
                break
        if buf:
            e.add_field(name=f"Meaning ({pos})", value="\n".join(buf)[:1024], inline=False)

    urls = entry.get("sourceUrls", [])
    if urls:
        e.add_field(name="Source", value=", ".join(urls)[:1024], inline=False)
    return e

def _build_simple_embed(data: Any, word: str):
    try:
        definition = data[0]["meanings"][0]["definitions"][0]["definition"]
    except Exception:
        return error_embed("Definition not available.")
    return result_embed(f"🔍 Definition of **{word}**", definition)

async def fetch_definition(word: str, full: bool = False):
    async with aiohttp.ClientSession() as session:
        async with session.get(DICTIONARY_URL.format(word)) as resp:
            if resp.status != 200:
                return error_embed("🙅 Word definition not found.")
            data = await resp.json()

    return _build_full_embed(data, word) if full else _build_simple_embed(data, word)
