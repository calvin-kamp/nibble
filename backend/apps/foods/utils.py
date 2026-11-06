import re

BARCODE_PATTERN = r"^[0-9]{8,14}$"
# Barcode, or the code of a generic food without one, e.g. "n00002" for a banana.
PRODUCT_CODE_PATTERN = r"^(?:[0-9]{8,14}|n[0-9]{5})$"


def normalize_barcode(value):
    """Barcode without spaces and hyphens, e.g. "4 260556 635439" -> "4260556635439"."""
    return re.sub(r"[\s-]", "", value)


def has_valid_check_digit(code):
    """GS1 check digit (EAN-8, UPC-A, EAN-13, GTIN-14), catches most typos."""
    if not re.fullmatch(BARCODE_PATTERN, code) or len(code) not in (8, 12, 13, 14):
        return False

    *body, check = map(int, code)
    # From the right, the digits next to the check digit count three times.
    total = sum(digit * (3 if index % 2 == 0 else 1) for index, digit in enumerate(reversed(body)))

    return (10 - total % 10) % 10 == check


def repair_mojibake(text):
    """Undoes UTF-8 read as Latin-1, e.g. "GÃ¼ldenhof" -> "Güldenhof"."""
    if not text or "Ã" not in text:
        return text

    try:
        return text.encode("latin-1").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return text


# "2.29€", "€ 2,29", "15.27 EUR"
PRICE_PATTERN = re.compile(
    r"(?:€\s*\d+(?:[.,]\d{1,2})?|\d+(?:[.,]\d{1,2})?\s*(?:€|eur\b|euro\b))", re.IGNORECASE
)
# "150g", "1 kg", "0,5l", "6 x 0.33 l", "1kg" of a base price; also "e" after the amount.
AMOUNT_PATTERN = re.compile(
    r"(?<![\w.,])(?:\d+\s*[x×]\s*)?\d+(?:[.,]\d+)?\s*(?:kg|mg|g|ml|cl|dl|l)\b\.?\s*e?\b",
    re.IGNORECASE,
)
# A word in capitals only, e.g. "GÜLDENHOF"; short ones like "BIO" or "XXL" stay.
SHOUTED_WORD_PATTERN = re.compile(r"\b[A-ZÄÖÜ][A-ZÄÖÜß]{3,}\b")
SEPARATOR_PATTERN = re.compile(r"^[\s,;:/|–-]+|[\s,;:/|–-]+$")


def clean_product_name(name, brand=None):
    """Name for the search without price, amounts and a leading brand.

    E.g. "ALDI GÜLDENHOF HUHN Hähnchenbrustfilet 150g 2.29€ 1kg 15.27€" with brand "Aldi"
    becomes "Güldenhof Huhn Hähnchenbrustfilet". Falls back to the original if nothing is left.
    """
    original = " ".join((name or "").split())
    cleaned = PRICE_PATTERN.sub(" ", original)
    cleaned = AMOUNT_PATTERN.sub(" ", cleaned)
    cleaned = " ".join(cleaned.split())

    if brand:
        prefix = brand.strip()

        if prefix and cleaned.lower().startswith(prefix.lower() + " "):
            cleaned = cleaned[len(prefix) :]

    cleaned = SEPARATOR_PATTERN.sub("", cleaned)

    # Only when the name has lower case letters too; a name in capitals throughout stays.
    if any(char.islower() for char in cleaned):
        cleaned = SHOUTED_WORD_PATTERN.sub(lambda match: match[0].capitalize(), cleaned)

    return cleaned or original
