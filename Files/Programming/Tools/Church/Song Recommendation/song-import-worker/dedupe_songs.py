import json


with open("metadata_results.json", "r", encoding="utf-8") as f:
    songs = json.load(f)


unique_map = {}

duplicates = []


for song in songs:
    cleaned_title = (
        song.get("cleaned_title")
        or song.get("extracted_title")
    )

    if not cleaned_title:
        continue

    key = cleaned_title.lower().strip()

    if key not in unique_map:
        unique_map[key] = song
    else:
        duplicates.append({
            "duplicate": song["youtube_title"],
            "matched_with": unique_map[key]["youtube_title"],
            "cleaned_title": cleaned_title
        })


unique_songs = list(unique_map.values())


with open("unique_songs.json", "w", encoding="utf-8") as f:
    json.dump(unique_songs, f, ensure_ascii=False, indent=2)


with open("duplicates.json", "w", encoding="utf-8") as f:
    json.dump(duplicates, f, ensure_ascii=False, indent=2)


print(f"\nOriginal songs: {len(songs)}")
print(f"Unique songs: {len(unique_songs)}")
print(f"Duplicates removed: {len(duplicates)}")

print("\nSaved:")
print("- unique_songs.json")
print("- duplicates.json")