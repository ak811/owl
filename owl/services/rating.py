import re
from typing import List, Tuple

from owl.services.gpt_utils import get_client

NUM_EMOJIS = {
    "0": "0️⃣", "1": "1️⃣", "2": "2️⃣", "3": "3️⃣",
    "4": "4️⃣", "5": "5️⃣", "6": "6️⃣", "7": "7️⃣",
    "8": "8️⃣", "9": "9️⃣"
}

EMOJI_RE = re.compile(
    "[\U0001F600-\U0001F64F"
    "\U0001F300-\U0001F5FF"
    "\U0001F680-\U0001F6FF"
    "\U0001F1E0-\U0001F1FF"
    "\U00002700-\U000027BF"
    "\U0001F900-\U0001F9FF"
    "\U00002600-\U000026FF]+", flags=re.UNICODE
)

def extract_emojis(text: str, max_emojis: int = 5) -> List[str]:
    return EMOJI_RE.findall(text)[:max_emojis]

async def rate_message_and_emojis(content: str) -> Tuple[str, List[str]]:
    prompt = (
        "You are Owl 🦉, a sharp and witty judge. "
        "First, rate the following message with a single digit based on how cool (0–9). "
        "Then, suggest 5 emoji reactions (funny, emotional, expressive) matching the vibe.\n\n"
        "Format:\n"
        "Rating: <digit>\n"
        "Emojis: 😬 🔥 💯 🤡 🧠\n\n"
        f"Message:\n\"{content.strip()}\""
    )

    client = get_client()
    res = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=40,
    )
    text = res.choices[0].message.content.strip()

    m = re.search(r"Rating:\s*([0-9])", text)
    score = m.group(1) if m else "0"
    em_line = re.search(r"Emojis:\s*(.+)", text)
    emojis = extract_emojis(em_line.group(1)) if em_line else []
    return score, emojis

def digit_to_emoji(score: str) -> str | None:
    return NUM_EMOJIS.get(score)
