import json
import ollama


MODEL_NAME = "qwen2.5:3b"


def extract_song_title(raw_title: str):
    try:
        response = ollama.chat(
            model=MODEL_NAME,

            messages=[
                {
                    "role": "user",
                    "content": f"""
Extract ONLY the actual Christian song title from this YouTube title.

Rules:
- Remove artist names
- Remove album names
- Remove promotional text
- Remove words like:
  official, lyrical, video, worship, gospel, remix, 4k
- Prefer Romanized English titles if available
- If not a real song title:
  return NOT_A_SONG

Input:
{raw_title}
"""
                }
            ],

            format={
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string"
                    }
                },
                "required": ["title"]
            }
        )

        content = response["message"]["content"]

        parsed = json.loads(content)

        title = parsed.get("title", "").strip()

        if title.lower() in [
            "",
            "none",
            "null",
            "unknown",
            "not_a_song"
        ]:
            return None

        return title

    except Exception as e:
        print("ERROR:", e)
        return None