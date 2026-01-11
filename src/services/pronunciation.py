import os
from gtts import gTTS

ACCENT_MAP = {
    "us": "com", "uk": "co.uk", "au": "com.au",
    "in": "co.in", "ca": "ca", "ie": "ie", "za": "co.za",
}

def build_tts(word: str, accent: str = "us") -> str:
    tld = ACCENT_MAP.get(accent.lower(), "com")
    safe = word.lower().replace(" ", "_")
    filename = f"{safe}.mp3" if accent.lower() == "us" else f"{safe}_{accent.lower()}.mp3"
    tts = gTTS(text=word, lang="en", tld=tld)
    tts.save(filename)
    return filename

def cleanup_file(path: str):
    try:
        if os.path.exists(path):
            os.remove(path)
    except Exception:
        pass
