import json
import re
import uuid

INPUT_FILE = "output/songs.json"
OUTPUT_FILE = "output/normalized_songs.json"


def clean_text(text):
    if not text:
        return ""

    # remove null chars
    text = text.replace("\u0000", "")

    # remove footer noise
    text = re.sub(r"go to index", "", text, flags=re.IGNORECASE)

    # normalize line endings
    text = text.replace("\r", "\n")

    # remove excessive blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)

    # remove trailing spaces on each line
    lines = [line.strip() for line in text.split("\n")]

    # remove empty junk lines
    lines = [line for line in lines if line]

    return "\n".join(lines).strip()



def normalize_title(title):
    title = title.lower()
    title = re.sub(r"[^a-z0-9\s]", "", title)
    title = re.sub(r"\s+", " ", title)

    return title.strip()


with open(INPUT_FILE, "r", encoding="utf-8") as f:
    songs = json.load(f)


unique_songs = {}

for song in songs:

    title = clean_text(song.get("title", ""))
    native = clean_text(song.get("lyrics_native", ""))
    english = clean_text(song.get("lyrics_english", ""))

    normalized_title = normalize_title(title)

    # secondary fingerprint
    fingerprint = normalized_title + native[:200]

    if fingerprint in unique_songs:
        continue

    unique_songs[fingerprint] = {
        "song_id": str(uuid.uuid4()),
        "title": title,
        "normalized_title": normalized_title,
        "lyrics_native": native,
        "lyrics_english": english,
        "language": song.get("language", "Unknown")
    }


final_songs = list(unique_songs.values())

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(final_songs, f, ensure_ascii=False, indent=2)


print(f"Original songs: {len(songs)}")
print(f"Unique songs: {len(final_songs)}")