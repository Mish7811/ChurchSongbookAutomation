import json


with open("cleaned_metadata.json", "r", encoding="utf-8") as f:
    songs = json.load(f)


for song in songs[:200]:
    print(song["title"])