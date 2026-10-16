"""Нормализация и проверка идентификаторов публикаций."""

import re

from src.models import Publication

ISSN_PATTERN = re.compile(r"[0-9]{7}[0-9X]")
DOI_PATTERN = re.compile(r"10\.[0-9]{4,9}/\S+")
DOI_PREFIXES = (
    "https://doi.org/",
    "http://doi.org/",
    "https://dx.doi.org/",
    "http://dx.doi.org/",
    "doi:",
)


def normalize_issn(value: str | None) -> str | None:
    """Удаляет пробелы и дефисы, возвращает ISSN в верхнем регистре."""
    if not isinstance(value, str):
        return None

    chars = re.sub(r"[\s-]", "", value).upper()
    return chars if ISSN_PATTERN.fullmatch(chars) else None


def normalize_doi(value: str | None) -> str | None:
    """Нормализует DOI и проверяет его формат."""
    if not isinstance(value, str):
        return None

    doi = value.strip().lower()
    if not doi:
        return None

    for prefix in DOI_PREFIXES:
        if doi.startswith(prefix):
            doi = doi[len(prefix) :]
            break

    return doi if DOI_PATTERN.fullmatch(doi) else None


def issn_check_digit_ok(issn: str | None) -> bool:
    """Проверяет контрольный разряд ISSN."""
    normalized = normalize_issn(issn)
    if normalized is None:
        return False

    weighted_sum = sum(
        int(digit) * weight
        for digit, weight in zip(normalized[:7], range(8, 1, -1))
    )
    check_value = (11 - weighted_sum % 11) % 11
    expected = "X" if check_value == 10 else str(check_value)

    return normalized[-1] == expected


def find_duplicates(publications: list[Publication]) -> list[str]:
    """Возвращает DOI, встречающиеся более одного раза."""
    seen: set[str] = set()
    duplicates: list[str] = []
    duplicate_set: set[str] = set()

    for publication in publications:
        if not isinstance(publication, Publication):
            continue

        doi = normalize_doi(publication.doi)
        if doi is None:
            continue

        if doi in seen and doi not in duplicate_set:
            duplicates.append(doi)
            duplicate_set.add(doi)

        seen.add(doi)

    return duplicates
