import logging
import re
from typing import Tuple

import fasttext

from owl.config import FASTTEXT_MODEL_PATH
from owl.services.gpt_utils import get_client

_FASTTEXT: fasttext.FastText | None = None

def _load_model() -> fasttext.FastText:
    global _FASTTEXT
    if _FASTTEXT is None:
        _FASTTEXT = fasttext.load_model(FASTTEXT_MODEL_PATH)
    return _FASTTEXT

def clean_mentions(text: str) -> str:
    text = re.sub(r"<@!?[0-9]+>", "", text)
    text = text.replace("\r", "").replace("\u200b", "")
    return text.strip()

def detect_language(text: str) -> Tuple[str, float]:
    model = _load_model()
    cleaned = clean_mentions(text).replace("\n", " ").strip()
    prediction = model.predict(cleaned, k=1)
    lang_code = prediction[0][0].replace("__label__", "")
    confidence = float(prediction[1][0])
    logging.getLogger("owl.translation").info(f"Detected {lang_code} ({confidence:.2f}) for: {cleaned}")
    return lang_code, confidence

def get_flag(lang_code: str) -> str:
    flags = {
        "en": "🇺🇸", "fr": "🇫🇷", "es": "🇪🇸", "de": "🇩🇪", "it": "🇮🇹", "pt": "🇵🇹",
        "ar": "🇸🇦", "fa": "🇮🇷", "zh": "🇨🇳", "ru": "🇷🇺", "ko": "🇰🇷",
        "ja": "🇯🇵", "tr": "🇹🇷", "hi": "🇮🇳"
    }
    return flags.get(lang_code.lower(), "🌐")

async def translate_to_english(text: str) -> str:
    prompt = f"Translate the following to natural English. Only return the translation:\n\n\"{text.strip()}\""
    client = get_client()
    res = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=120,
    )
    return res.choices[0].message.content.strip()
