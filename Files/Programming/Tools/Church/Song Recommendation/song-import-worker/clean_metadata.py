import json

from normalize import (
    normalize_title,
    normalize_artist,
    is_junk_title,
    is_junk_artist,
)


with open("metadata_results.json", "r", encoding="utf-8") as f:
    songs = json.load(f)


cleaned = []

removed = 0


for song in songs:
    title = normalize_title(song.get("extracted_title", ""))
    artist = normalize_artist(song.get("artist", ""))

    if is_junk_title(title):
        removed += 1
        continue

    if is_junk_artist(artist):
        artist = ""

    cleaned.append({
        "video_id": song.get("video_id"),
        "youtube_title": song.get("youtube_title"),
        "url": song.get("url"),

        "title": title,
        "artist": artist,
    })


with open("cleaned_metadata.json", "w", encoding="utf-8") as f:
    json.dump(cleaned, f, ensure_ascii=False, indent=2)


print(f"\nCleaned songs: {len(cleaned)}")
print(f"Removed junk entries: {removed}")