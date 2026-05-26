from indic_transliteration import sanscript
from indic_transliteration.sanscript import transliterate


def transliterate_to_english(text: str):
    try:
        return transliterate(
            text,
            sanscript.TAMIL,
            sanscript.ITRANS
        )

    except Exception:
        return text