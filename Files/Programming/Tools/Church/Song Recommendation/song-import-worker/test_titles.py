from metadata_extractor import extract_song_title


samples = [
    "Giftson Durai - En Iravo En Pagalo (Official Music Video)",

    "NEW TELUGU CHRISTIAN SONGS SANTHOSHAME NA YESUNILO DAVIDSON",

    "Raj Prakash Paul Jessy Paul",

    "DHAYAVAAL PETTRAEN ( Official ) || JOHNSAM JOYSON || TAMIL CHRISTIAN SONGS || தயவால் பெற்றேன்",

    "Jeeva R Pakerla & Febin Chacko - Varama Lyrical Song Srastha-3"
]


for s in samples:
    print("\nRAW:")
    print(s)

    print("\nEXTRACTED:")
    print(extract_song_title(s))