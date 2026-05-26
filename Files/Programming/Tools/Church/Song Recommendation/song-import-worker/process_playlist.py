import json
import os
import time

from main import extract_playlist_videos
from metadata_extractor import extract_song_title


SAVE_EVERY = 100


def process_playlist(playlist_url):
    videos = extract_playlist_videos(playlist_url)

    print(f"\nFound {len(videos)} videos\n")

    # Load previous progress if exists
    if os.path.exists("metadata_results.json"):
        with open("metadata_results.json", "r", encoding="utf-8") as f:
            results = json.load(f)

        processed_titles = {
            item["youtube_title"]
            for item in results
        }

        print(f"Loaded {len(results)} existing results\n")

    else:
        results = []
        processed_titles = set()

    for index, video in enumerate(videos):
        raw_title = video["title"]

        # Skip already processed
        if raw_title in processed_titles:
            print(f"SKIPPED: {raw_title}")
            continue

        cleaned_title = extract_song_title(raw_title)

        if not cleaned_title["success"]:
            print(f"FAILED: {raw_title}")

        result = {
            "video_id": video["video_id"],
            "youtube_title": raw_title,
            "url": video["url"],
            "cleaned_title": cleaned_title
        }

        results.append(result)

        print(f"[{len(results)}/{len(videos)}]")
        print(result)
        print()

        # Save every N songs
        if len(results) % SAVE_EVERY == 0:
            with open("metadata_results.json", "w", encoding="utf-8") as f:
                json.dump(results, f, ensure_ascii=False, indent=2)

            print(f"Checkpoint saved at {len(results)} songs\n")

        # Prevent overwhelming local inference
        time.sleep(0.2)

    # Final save
    with open("metadata_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print("\nDone.")
    print("Saved to metadata_results.json")


if __name__ == "__main__":
    playlist_url = input("Enter playlist URL: ")

    process_playlist(playlist_url)