from yt_dlp import YoutubeDL
from title_cleaner import clean_song_title, contains_english, extract_primary_title, extract_probable_song_title


def extract_playlist_videos(playlist_url):
    ydl_opts = {
        "quiet": True,
        "extract_flat": True,
        "skip_download": True,
    }

    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(playlist_url, download=False)

    videos = []

    for entry in info["entries"]:
        videos.append({
            "video_id": entry.get("id"),
            "title": entry.get("title"),
            "url": f"https://www.youtube.com/watch?v={entry.get('id')}"
        })

    return videos


if __name__ == "__main__":
    playlist_url = input("Enter playlist URL: ")

    videos = extract_playlist_videos(playlist_url)

    print(f"\nFound {len(videos)} videos\n")

    for video in videos[:20]:
        raw_title = video["title"]

        primary_title = extract_probable_song_title(raw_title)

        has_english = contains_english(raw_title)

        print("\nRAW:")
        print(raw_title)

        print("PRIMARY TITLE:")
        print(primary_title)

        print("HAS ENGLISH:")
        print(has_english)

        cleaned = clean_song_title(raw_title)

        print("CLEANED:")
        print(cleaned)