# owl/services/definitions.py
import json
import re
from typing import Any, Dict, List, Optional, Tuple

from owl.embeds import base_embed, result_embed, error_embed
from owl.services.gpt_utils import get_client

# ---------------- LLM prompts ----------------

_SYSTEM = (
    "You are an expert English lexicographer. "
    "Given a word or short phrase, return concise, modern explanations. "
    "Put the most common, general meanings first. Keep examples short and natural."
)

_JSON_INSTRUCTIONS = (
    "Respond in STRICT JSON with keys: word (string), entries (array of 1-5 objects). "
    "Each entry object MUST have: pos (string, lowercase like 'noun' or 'verb'), "
    "meaning (string <= 22 words, simple wording), synonyms (array of 0-5 short strings), "
    "antonyms (array of 0-5 short strings), example (string <= 16 words). "
    "No markdown, no commentary—JSON only."
)

# ---------------- Utilities ----------------

def _strip_code_fences(text: str) -> str:
    if text.startswith("```"):
        # remove ```json ... ``` wrappers if the model added them
        return re.sub(r"^```(?:json)?\s*|\s*```$", "", text.strip(), flags=re.IGNORECASE)
    return text.strip()

def _safe_json_loads(text: str) -> Optional[Dict[str, Any]]:
    # First try straight parse (after stripping code fences)
    txt = _strip_code_fences(text)
    try:
        return json.loads(txt)
    except Exception:
        pass
    # Try to salvage the first JSON object found
    m = re.search(r"\{.*\}", txt, flags=re.DOTALL)
    if m:
        try:
            return json.loads(m.group(0))
        except Exception:
            pass
    return None

def _clean_entries(raw_entries: List[Dict[str, Any]], max_entries: int) -> List[Dict[str, Any]]:
    cleaned: List[Dict[str, Any]] = []
    for e in (raw_entries or [])[:max_entries]:
        if not isinstance(e, dict):
            continue
        pos = str(e.get("pos", "")).strip().lower() or "meaning"
        meaning = str(e.get("meaning", "")).strip()
        if not meaning:
            continue
        syns = [s.strip() for s in (e.get("synonyms") or []) if isinstance(s, str) and s.strip()][:5]
        ants = [a.strip() for a in (e.get("antonyms") or []) if isinstance(a, str) and a.strip()][:5]
        ex = e.get("example")
        example = str(ex).strip() if isinstance(ex, str) and ex.strip() else None
        cleaned.append({"pos": pos, "meaning": meaning, "synonyms": syns, "antonyms": ants, "example": example})
    return cleaned

async def _one_liner(word: str) -> str:
    client = get_client()
    prompt = (
        f"Give ONE short main meaning (<= 18 words) for: {word}\n"
        "Plain text only; no quotes."
    )
    res = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": _SYSTEM},
            {"role": "user", "content": prompt},
        ],
        max_tokens=60,
        temperature=0.2,
    )
    text = (res.choices[0].message.content or "").strip()
    return text

# ---------------- Core query ----------------

async def _query_lexicon(word: str, max_entries: int) -> Dict[str, Any]:
    """
    Ask the LLM for compact dictionary data, robust to JSON hiccups.
    Always returns at least one usable entry.
    """
    client = get_client()
    user_prompt = f"Word: {word}\nMax entries: {max_entries}\n\n{_JSON_INSTRUCTIONS}"

    # Pass 1: strict JSON mode
    res = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": _SYSTEM}, {"role": "user", "content": user_prompt}],
        response_format={"type": "json_object"},
        max_tokens=500,
        temperature=0.2,
    )
    parsed = _safe_json_loads(res.choices[0].message.content or "")
    if not parsed:
        # Pass 2: retry with simpler guidance (still JSON mode)
        res2 = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": _SYSTEM},
                {"role": "user",
                 "content": f"Word: {word}\nReturn 1-4 entries.\n{_JSON_INSTRUCTIONS}"},
            ],
            response_format={"type": "json_object"},
            max_tokens=400,
            temperature=0.2,
        )
        parsed = _safe_json_loads(res2.choices[0].message.content or "")

    entries = _clean_entries((parsed or {}).get("entries") or [], max_entries)
    out_word = str((parsed or {}).get("word", word)).strip() or word

    if entries:
        return {"word": out_word, "entries": entries}

    # Final fallback: guarantee a valid single entry
    meaning = await _one_liner(word)
    fallback = {
        "word": out_word,
        "entries": [{
            "pos": "meaning",
            "meaning": meaning or "A commonly used English term.",
            "synonyms": [],
            "antonyms": [],
            "example": None,
        }]
    }
    return fallback

# ---------------- Embed builders ----------------

def _build_full_embed_from_entries(word: str, entries: List[Dict[str, Any]]):
    e = base_embed(f"🔍 Definition of **{word}**")
    for idx, item in enumerate(entries[:6], start=1):
        pos = item["pos"]
        meaning = item["meaning"]
        syns = item.get("synonyms") or []
        ants = item.get("antonyms") or []
        example = item.get("example")

        body_lines: List[str] = [f"**{idx}.** {meaning}"]
        if syns:
            body_lines.append(f"**Synonyms:** {', '.join(syns[:5])}")
        if ants:
            body_lines.append(f"**Antonyms:** {', '.join(ants[:5])}")
        if example:
            body_lines.append(f"*Example:* {example}")

        e.add_field(
            name=f"Meaning ({pos})",
            value="\n".join(body_lines)[:1024],
            inline=False,
        )
    return e

def _build_simple_embed_from_entries(word: str, entries: List[Dict[str, Any]]):
    primary = entries[0]
    return result_embed(f"🔍 Definition of **{word}**", primary["meaning"])

def _build_glossary_embed_from_entries(word: str, entries: List[Dict[str, Any]]):
    e = base_embed(f"📘 {word}: quick meanings")
    for item in entries[:3]:
        pos = item["pos"]
        meaning = item["meaning"]
        syns = item.get("synonyms") or []
        ants = item.get("antonyms") or []
        example = item.get("example")

        lines: List[str] = [f"**Meaning:** {meaning}"]
        if syns:
            lines.append(f"**Synonyms:** {', '.join(syns[:5])}")
        if ants:
            lines.append(f"**Antonyms:** {', '.join(ants[:5])}")
        if example:
            lines.append(f"**Example:** _{example}_")

        e.add_field(name=pos or "meaning", value="\n".join(lines)[:1024], inline=False)
    return e

# ---------------- Public functions ----------------

async def fetch_definition(word: str, full: bool = False):
    """
    Used by:
      - !owl def  (full=False)
      - !owl deff (full=True)
    Always uses GPT; no external dictionary API.
    """
    word = (word or "").strip()
    if not word:
        return error_embed("Please provide a word.")
    data = await _query_lexicon(word, max_entries=6 if full else 4)
    entries = data.get("entries", [])
    if not entries:
        # Should not happen, but keep a graceful fallback
        one = await _one_liner(word)
        return result_embed(f"🔍 Definition of **{word}**", one or "A commonly used English term.")
    return _build_full_embed_from_entries(data["word"], entries) if full \
        else _build_simple_embed_from_entries(data["word"], entries)

async def fetch_glossary(word: str):
    """
    Used by the dictionary-channel watcher.
    Always uses GPT; returns short meanings + syns/ants + one example each.
    """
    word = (word or "").strip()
    if not word:
        return error_embed("Please provide a word.")
    data = await _query_lexicon(word, max_entries=3)
    entries = data.get("entries", [])
    if not entries:
        one = await _one_liner(word)
        return result_embed(f"📘 {word}: quick meanings", one or "A commonly used English term.")
    return _build_glossary_embed_from_entries(data["word"], entries)
