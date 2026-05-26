import yt_dlp
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime

# -----------------------------
# DATABASE CONFIG
# -----------------------------
DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "church_songbook",
    "user": "postgres",
}

# -----------------------------
# YT-DLP CONFIG
# -----------------------------
YDL_OPTS = {
    "quiet": True,
    "skip_download": True,
}


# -----------------------------
# SIMPLE LYRICS HEURISTIC
# -----------------------------
def looks_like_lyrics(text: str) -> bool:
    if not text:
        return False

    lines = [line.strip() for line in text.splitlines() if line.strip()]

    # too short
    if len(lines) < 10:
        return False

    # enough meaningful lines
    meaningful_lines = [line for line in lines if len(line) > 5]

    if len(meaningful_lines) < 8:
        return False

    # reject descriptions with too many links
    link_count = text.count("http")

    if link_count > 5:
        return False

    return True


# -----------------------------
# FETCH DESCRIPTION
# -----------------------------
def fetch_description(youtube_url: str):
    try:
        with yt_dlp.YoutubeDL(YDL_OPTS) as ydl:
            info = ydl.extract_info(youtube_url, download=False)

        description = info.get("description", "")

        return description

    except Exception as e:
        print(f"[ERROR FETCHING] {youtube_url} -> {e}")
        return None


# -----------------------------
# MAIN
# -----------------------------
def main():
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    cursor.execute("""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name = 'intermediate_songs';
    """)
    
    columns = cursor.fetchall()
    
    print(columns)

    cursor.execute("""
        SELECT id, cleaned_title, youtube_url
        FROM intermediate_songs
        WHERE ingestion_status = 'ready_to_insert'
        AND lyrics_found = FALSE
        LIMIT 50;
    """)

    songs = cursor.fetchall()

    total = len(songs)
    found = 0
    not_found = 0
    errors = 0

    print(f"\nProcessing {total} songs...\n")

    for song in songs:
        song_id = song["id"]
        title = song["cleaned_title"]
        youtube_url = song["youtube_url"]

        print(f"\nChecking: {title}")

        try:
            description = fetch_description(youtube_url)

            if not description:
                cursor.execute("""
                    UPDATE intermediate_songs
                    SET
                        ingestion_status = 'lyrics_not_found',
                        last_lyrics_check = NOW()
                    WHERE id = %s;
                """, (str(song_id),))

                conn.commit()

                print("[NOT FOUND] Empty description")
                not_found += 1
                continue

            if looks_like_lyrics(description):

                cursor.execute("""
                    UPDATE intermediate_songs
                    SET
                        lyrics_found = TRUE,
                        raw_lyrics = %s,
                        lyrics_source = 'youtube_description',
                        lyrics_confidence = 0.7,
                        ingestion_status = 'lyrics_found',
                        last_lyrics_check = NOW(),
                        updated_at = NOW()
                    WHERE id = %s;
                """, (description, str(song_id)))

                conn.commit()

                print("[FOUND] Lyrics detected")
                found += 1

            else:
                cursor.execute("""
                    UPDATE intermediate_songs
                    SET
                        ingestion_status = 'lyrics_not_found',
                        last_lyrics_check = NOW(),
                        updated_at = NOW()
                    WHERE id = %s;
                """, (str(song_id),))

                conn.commit()

                print("[NOT FOUND] Doesn't look like lyrics")
                not_found += 1

        except Exception as e:
            print(f"[ERROR] {title} -> {e}")

            errors += 1

    print("\n==========================")
    print("DONE")
    print("==========================")
    print(f"Processed     : {total}")
    print(f"Lyrics Found  : {found}")
    print(f"Not Found     : {not_found}")
    print(f"Errors         : {errors}")

    if total > 0:
        print(f"Success Rate  : {(found / total) * 100:.2f}%")

    cursor.close()
    conn.close()


if __name__ == "__main__":
    main()