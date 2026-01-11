# owl/services/translation.py
import logging
import os
import re
from typing import Tuple

import fasttext

from src.config import FASTTEXT_MODEL_PATH
from src.services.gpt_utils import get_client

_FASTTEXT = None
_FT_URL = "https://dl.fbaipublicfiles.com/fasttext/supervised-models/lid.176.bin"

def _ensure_model_file(path: str) -> None:
    """Download lid.176.bin if it's missing."""
    if os.path.exists(path) and os.path.getsize(path) > 0:
        return
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    try:
        import urllib.request
        logging.getLogger("owl.translation").info(f"Downloading fastText model to {path} …")
        urllib.request.urlretrieve(_FT_URL, path)  # nosec - trusted FB CDN
    except Exception as e:
        raise RuntimeError(
            f"Could not download fastText model to {path}. "
            f"Download it manually from:\n{_FT_URL}\n"
            f"Or set FASTTEXT_MODEL_PATH in .env"
        ) from e

def _load_model():
    global _FASTTEXT
    if _FASTTEXT is None:
        path = FASTTEXT_MODEL_PATH or "models/lid.176.bin"
        _ensure_model_file(path)
        _FASTTEXT = fasttext.load_model(path)
    return _FASTTEXT

def clean_mentions(text: str) -> str:
    text = re.sub(r"<@!?[0-9]+>", "", text)
    text = text.replace("\r", "").replace("\u200b", "")
    return text.strip()

def detect_language(text: str) -> Tuple[str, float]:
    try:
        model = _load_model()
        cleaned = clean_mentions(text).replace("\n", " ").strip()
        prediction = model.predict(cleaned, k=1)
        lang_code = prediction[0][0].replace("__label__", "")
        confidence = float(prediction[1][0])
        logging.getLogger("owl.translation").info(f"Detected {lang_code} ({confidence:.2f}) for: {cleaned}")
        return lang_code, confidence
    except Exception as e:
        logging.getLogger("owl.translation").warning(f"fastText detection failed: {e}")
        # Fallback: unknown language; UI will show 🌐 and we still translate.
        return "und", 0.0

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
