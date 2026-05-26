import psycopg2

from rapidfuzz import fuzz


DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "church_songbook",
    "user": "postgres",
}


SIMILARITY_THRESHOLD = 90


conn = psycopg2.connect(**DB_CONFIG)

cursor = conn.cursor()


# Fetch existing production songs
cursor.execute("""
    SELECT song_id, normalized_title
    FROM songs
""")

existing_songs = cursor.fetchall()


print(f"Loaded {len(existing_songs)} existing songs")


# Fetch pending intermediate songs
cursor.execute("""
    SELECT id, cleaned_title
    FROM intermediate_songs
    WHERE ingestion_status = 'pending'
""")

intermediate_songs = cursor.fetchall()


print(f"Loaded {len(intermediate_songs)} intermediate songs")


matched = 0
unmatched = 0


for intermediate_id, cleaned_title in intermediate_songs:

    if not cleaned_title:
        continue

    best_score = 0
    best_match_id = None


    for existing_id, existing_title in existing_songs:

        if not existing_title:
            continue

        score = fuzz.token_sort_ratio(
            " ".join(cleaned_title.lower().split()),
            " ".join(existing_title.lower().split())
        )

        if score > best_score:
            best_score = score
            best_match_id = existing_id


    # Existing match found
    if best_score >= SIMILARITY_THRESHOLD:

        cursor.execute("""
            UPDATE intermediate_songs
            SET
                ingestion_status = 'matched_existing',
                matched_song_id = %s
            WHERE id = %s
        """, (
            best_match_id,
            intermediate_id
        ))

        matched += 1

        print(f"MATCHED: {cleaned_title} ({best_score})")

    else:

        cursor.execute("""
            UPDATE intermediate_songs
            SET ingestion_status = 'ready_to_insert'
            WHERE id = %s
        """, (
            intermediate_id,
        ))

        unmatched += 1

        print(f"NEW SONG: {cleaned_title}")


conn.commit()

cursor.close()
conn.close()


print("\nDone.")
print(f"Matched existing: {matched}")
print(f"Ready to insert: {unmatched}")