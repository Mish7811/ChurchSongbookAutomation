import pdfplumber
import re
import json
import os
from tqdm import tqdm

PDF_FOLDER = "pdfs"
OUTPUT_FILE = "output/songs.json"

# -------------------------------
# Helpers
# -------------------------------

def extract_text_from_pdf(path):
    pages = []
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                pages.append(text.strip())
    return pages

def is_noise_page(text):
    # Look for specific headings rather than broad keywords
    # This prevents the "Go to index" footer from triggering a false positive.
    noise_phrases = [
        "offering time",
        "sunday school",
        "songs index", 
        "blessed week"
    ]
    text_lower = text.lower()
    return any(phrase in text_lower for phrase in noise_phrases)

def clean_text(text):
    # 1. NEW: Remove null characters (OCR noise)
    text = text.replace("\u0000", "")
    
    # 2. Removes unwanted "Go to index" footers to keep the lyrics clean
    text = re.sub(r"Go to index|Go to the playlist", "", text, flags=re.IGNORECASE)
    
    # 3. Retains ASCII, Tamil, Telugu, and newlines
    text = re.sub(r"[^\x00-\x7F\u0B80-\u0BFF\u0C00-\u0C7F\n ]", "", text)
    
    # 4. Fix formatting noise (extra blank lines)
    text = re.sub(r"\n+", "\n", text)
    
    return text.strip()

def detect_language(text):
    if re.search(r"[\u0B80-\u0BFF]", text):
        return "Tamil"
    elif re.search(r"[\u0C00-\u0C7F]", text):
        return "Telugu"
    return "Unknown"

def extract_titles_from_index(pages):
    titles = []
    for page in pages:
        if "songs index" in page.lower():
            lines = page.split("\n")
            for line in lines:
                # Extracts titles matching format "1. Song Name"
                match = re.search(r"(\d+)\.\s*(.+)", line)
                if match:
                    titles.append(match.group(2).strip())
            break
    return titles

# -------------------------------
# Core Processing
# -------------------------------

def process_pdf(pdf_path, start_id):
    pages = extract_text_from_pdf(pdf_path)
    titles = extract_titles_from_index(pages)

    start_index = None

    # Find where the actual songs begin
    for i, page in enumerate(pages):
        if re.search(r"\bSong\s*\d+\b", page, re.IGNORECASE):
            start_index = i
            break

    if start_index is None:
        return [], start_id

    # -------------------------------
    # Extract songs in pairs
    # -------------------------------
    songs = []
    i = start_index

    while i < len(pages) - 1:
        native = pages[i]

        # skip noise pages
        if is_noise_page(native):
            i += 1
            continue

        # ensure it's a real song page
        if re.search(r"\bSong\s*\d+\b", native, re.IGNORECASE):
            english = pages[i + 1]
            songs.append((native, english))
            i += 2  # Skip ahead by 2 since we consumed a pair
        else:
            i += 1

    # -------------------------------
    # Structure songs
    # -------------------------------
    structured_songs = []
    song_id = start_id

    for idx, (native, english) in enumerate(songs):
        native_clean = clean_text(native)
        english_clean = clean_text(english)

        # Fallback to generic title if index extraction misses a count
        title = titles[idx] if idx < len(titles) else f"Song {song_id}"
        language = detect_language(native_clean)

        # Remove "SONG X" headers from the final lyrics
        native_clean = re.sub(r"^SONG\s*\d+\s*", "", native_clean, flags=re.IGNORECASE).strip()
        english_clean = re.sub(r"^SONG\s*\d+\s*", "", english_clean, flags=re.IGNORECASE).strip()

        structured_songs.append({
            "id": song_id,
            "title": title,
            "lyrics_native": native_clean,
            "lyrics_english": english_clean,
            "language": language
        })

        song_id += 1

    return structured_songs, song_id

# -------------------------------
# Main Runner
# -------------------------------

def main():
    all_songs = []
    song_id = 1

    for file in tqdm(os.listdir(PDF_FOLDER)):
        if file.endswith(".pdf"):
            path = os.path.join(PDF_FOLDER, file)
            
            # NEW: Try/Except block to protect the batch run
            try:
                songs, song_id = process_pdf(path, song_id)
                all_songs.extend(songs)
            except Exception as e:
                print(f"\n⚠️ Error processing {file}: {e}")

    os.makedirs("output", exist_ok=True)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(all_songs, f, ensure_ascii=False, indent=2)

    print(f"✅ Extracted {len(all_songs)} songs!")

if __name__ == "__main__":
    main()