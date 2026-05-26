from transliterator import transliterate_to_english


samples = [
    "தயவால் பெற்றேன்",
    "பிரியாமல் கடைசி வரை",
    "மாயையான வாழ்க்கை"
]


for s in samples:
    print("\nORIGINAL:")
    print(s)

    print("TRANSLITERATED:")
    print(transliterate_to_english(s))