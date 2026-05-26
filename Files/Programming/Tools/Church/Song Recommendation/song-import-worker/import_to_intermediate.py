import json
import psycopg2


DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "church_songbook",
    "user": "postgres",
}


with open("unique_songs.json", "r", encoding="utf-8") as f:
    songs = json.load(f)

print(f"Loaded songs: {len(songs)}")

print(songs[:3])


conn = psycopg2.connect(**DB_CONFIG)

cursor = conn.cursor()


inserted = 0
skipped = 0


for song in songs:
    cleaned_title = (
        song.get("cleaned_title")
        or song.get("extracted_title")
    )

    if not cleaned_title:
        skipped += 1
        continue

    youtube_title = song.get("youtube_title")
    youtube_url = song.get("url")
    video_id = song.get("video_id")

    # Prevent duplicate inserts
    cursor.execute(
        """
        SELECT id
        FROM intermediate_songs
        WHERE youtube_video_id = %s
        """,
        (video_id,)
    )

    existing = cursor.fetchone()

    if existing:
        skipped += 1
        continue

    cursor.execute(
        """
        INSERT INTO intermediate_songs (
            cleaned_title,
            original_youtube_title,
            youtube_video_id,
            youtube_url,
            ingestion_status
        )
        VALUES (%s, %s, %s, %s, %s)
        """,
        (
            cleaned_title,
            youtube_title,
            video_id,
            youtube_url,
            "pending"
        )
    )

    inserted += 1


conn.commit()

cursor.close()
conn.close()


print(f"\nInserted: {inserted}")
print(f"Skipped: {skipped}")