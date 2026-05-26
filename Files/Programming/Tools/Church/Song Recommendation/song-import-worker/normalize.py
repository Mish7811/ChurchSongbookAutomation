import re


JUNK_TITLES = {
    "private video",
    "deleted video",
    "official video",
    "latest telugu christian song",
    "latest telugu christian songs",
    "latest worship song",
    "tamil christian song",
    "telugu christian song",
    "christian song",
    "worship song",
    "gospel song",
}


JUNK_ARTISTS = {
    "",
    "unknown",
    "unknown artist",
    "<artist name>",
    "<unknown artist>",
    "<removed>",
    "preserved exactly as given",
}


REMOVE_PATTERNS = [
    r"\(official.*?\)",
    r"\[official.*?\]",
    r"official music video",
    r"official video",
    r"lyrical video",
    r"music video",
    r"video song",
    r"full song",
    r"4k",
    r"hd",
    r"\b20\d{2}\b",
]


def clean_whitespace(text: str):
    return re.sub(r"\s+", " ", text).strip()


def normalize_title(title: str):
    if not title:
        return ""

    title = title.strip()

    for pattern in REMOVE_PATTERNS:
        title = re.sub(pattern, "", title, flags=re.IGNORECASE)

    title = re.sub(r"[❤️🔥✨🎵🎶]", "", title)

    title = re.sub(r"\|+", " ", title)

    title = re.sub(r"\s+", " ", title)

    return title.strip()


def normalize_artist(artist: str):
    if not artist:
        return ""

    artist = artist.strip()

    artist = artist.replace("||", "|")

    artist = re.sub(r"\s*\|\s*", " | ", artist)

    artist = re.sub(r"\s+", " ", artist)

    return artist.strip()


def is_junk_title(title: str):
    if not title:
        return True

    normalized = title.lower().strip()

    if normalized in JUNK_TITLES:
        return True

    if len(normalized) <= 2:
        return True

    return False


def is_junk_artist(artist: str):
    normalized = artist.lower().strip()

    return normalized in JUNK_ARTISTS