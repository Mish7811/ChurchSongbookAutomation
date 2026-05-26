import json

from rapidfuzz import fuzz


SIMILARITY_THRESHOLD = 85


with open("cleaned_metadata.json", "r", encoding="utf-8") as f:
    songs = json.load(f)


duplicates = []
checked_pairs = set()


for i, song1 in enumerate(songs):
    title1 = (song1.get("extracted_title") or "").strip().lower()

    if not title1:
        continue

    for j, song2 in enumerate(songs[i + 1:], start=i + 1):
        title2 = (song2.get("extracted_title") or "").strip().lower()

        if not title2:
            continue

        # Prevent duplicate comparisons
        pair_key = tuple(sorted([title1, title2]))

        if pair_key in checked_pairs:
            continue

        checked_pairs.add(pair_key)

        score = fuzz.token_sort_ratio(title1, title2)

        if score >= 80:
            print(title1, " <-> ", title2, " = ", score)

        if score >= SIMILARITY_THRESHOLD:
            duplicates.append({
                "title_1": song1["extracted_title"],
                "title_2": song2["extracted_title"],
                "score": score,

                "artist_1": song1.get("artist", ""),
                "artist_2": song2.get("artist", ""),
            })


print(f"\nFound {len(duplicates)} possible duplicates\n")


for dup in duplicates[:50]:
    print("====================")
    print(f"TITLE 1: {dup['title_1']}")
    print(f"TITLE 2: {dup['title_2']}")
    print(f"SCORE: {dup['score']}")

    print(f"ARTIST 1: {dup['artist_1']}")
    print(f"ARTIST 2: {dup['artist_2']}")
    print()


with open("duplicates.json", "w", encoding="utf-8") as f:
    json.dump(duplicates, f, ensure_ascii=False, indent=2)


print("Saved duplicates to duplicates.json")