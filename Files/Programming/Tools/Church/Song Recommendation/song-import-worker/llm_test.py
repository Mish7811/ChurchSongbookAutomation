from metadata_extractor import extract_metadata


titles = [
    "Giftson Durai - En Iravo En Pagalo (Official Music Video)",

    "Jeby Israel - Enakkai Yutham Seibavar | எனக்காய் யுத்தம் செய்பவர் | New Tamil Christian Song | 2021",

    "DHAYAVAAL PETTRAEN ( Official ) || JOHNSAM JOYSON || TAMIL CHRISTIAN SONGS || தயவால் பெற்றேன்",

    "PIRIYAMAL KADAISIVARAI | பிரியாமல் கடைசி வரை | WORSHIP SERIES 2 |4K",

    "மாயையான வாழ்க்கை | Evangelist Sam Prasad | Tamil Christian Song"
]


for raw_title in titles:
    result = extract_metadata(raw_title)

    print("\n====================")
    print("RAW:")
    print(raw_title)

    print("\nEXTRACTED:")
    print(result)