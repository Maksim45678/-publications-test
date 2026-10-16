import re

ISSN_PATTERN = re.compile(r"[0-9]{7}[0-9X]")


def normalize_issn(value):
    """Нормализует ISSN или возвращает None для непригодного значения."""
    if value is None:
        return None

    try:
        chars = value.upper().replace("-", "").replace(" ", "")
    except AttributeError:
        return None

    return chars if ISSN_PATTERN.fullmatch(chars) else None
