import re


JUNK_PATTERNS = [
    r"\(official.*?\)",
    r"\bofficial\b",
    r"\bmusic video\b",
    r"\bmusic\b",
    r"\bvideo\b",
    r"\blyrical\b",
    r"\b4k\b",
    r"\bhd\b",

    r"\b(tamil|telugu|english)\s+(christian\s+)?(motivational\s+)?song[s]?\b",
    r"\bgospel\b",

    r"\bnew\b",
    r"\blatest\b",

    r"\bworship series\b",
    r"\bvol\.?\s?\d+\b",

    r"\b202\d\b",
]

def extract_probable_song_title(raw_title: str):
    # Split by pipe first
    pipe_parts = [p.strip() for p in raw_title.split("|") if p.strip()]

    first_part = pipe_parts[0]

    # Handle Artist - Song pattern
    if " - " in first_part:
        dash_parts = first_part.split(" - ")

        if len(dash_parts) >= 2:
            return dash_parts[1].strip()

    return first_part.strip()

def extract_primary_title(raw_title: str):
    parts = raw_title.split("|")

    if not parts:
        return raw_title

    return parts[0].strip()

def contains_english(text):
    return bool(re.search(r"[a-zA-Z]", text))

def clean_song_title(title: str):
    cleaned = title.lower()

    # Replace separators
    cleaned = re.sub(r"[\-|_/]", " ", cleaned)

    # Remove junk patterns
    for pattern in JUNK_PATTERNS:
        cleaned = re.sub(pattern, "", cleaned)

    # Keep ONLY English letters + numbers
    cleaned = re.sub(r"[^a-zA-Z0-9\s]", "", cleaned)

    # Remove extra spaces
    cleaned = re.sub(r"\s+", " ", cleaned).strip()

    # Remove trailing standalone numbers
    cleaned = re.sub(r"\b\d+\b$", "", cleaned).strip()

    return cleaned