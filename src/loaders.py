"""Загрузка, входной контроль и преобразование данных публикаций."""

import csv
import json
from collections.abc import Sequence
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from src.models import Publication
from src.normalize import normalize_doi, normalize_issn

RejectedRecord = tuple[str | None, str]


class CrossrefAuthor(BaseModel):
    """Данные автора из Crossref."""

    model_config = ConfigDict(extra="ignore")

    family: str | None = None
    given: str | None = None


class CrossrefDate(BaseModel):
    """Дата публикации в формате Crossref."""

    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    date_parts: list[list[int | None]] = Field(alias="date-parts")


class CrossrefWork(BaseModel):
    """Схема входящей записи Crossref."""

    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    DOI: str
    title: list[str] = Field(min_length=1)
    ISSN: list[str] = Field(default_factory=list)
    container_title: list[str] = Field(
        default_factory=list,
        alias="container-title",
    )
    author: list[CrossrefAuthor] = Field(default_factory=list)
    issued: CrossrefDate | None = None


class OpenAlexSource(BaseModel):
    """Описание научного издания в OpenAlex."""

    model_config = ConfigDict(extra="ignore")

    display_name: str | None = None
    issn_l: str | None = None
    issn: list[str] | None = None


class OpenAlexLocation(BaseModel):
    """Основное место публикации в OpenAlex."""

    model_config = ConfigDict(extra="ignore")

    source: OpenAlexSource | None = None


class OpenAlexWork(BaseModel):
    """Схема записи OpenAlex."""

    model_config = ConfigDict(extra="ignore")

    doi: str | None = None
    title: str | None = None
    publication_year: int | None = None
    primary_location: OpenAlexLocation | None = None


def load_items(path: str | Path) -> list[dict[str, Any]]:
    """Читает JSON-ответ Crossref и возвращает message.items."""
    with Path(path).open("r", encoding="utf-8") as file:
        payload = json.load(file)

    if not isinstance(payload, dict):
        raise TypeError("Ожидался JSON-объект с ключом message")

    message = payload.get("message")
    if not isinstance(message, dict):
        raise TypeError("В JSON отсутствует объект message")

    items = message.get("items")
    if not isinstance(items, list):
        raise TypeError("В объекте message отсутствует список items")

    if any(not isinstance(item, dict) for item in items):
        raise ValueError("Каждый элемент items должен быть JSON-объектом")

    return items


def _doi_for_log(value: object) -> str | None:
    """Подготавливает DOI для записи в журнал."""
    if value is None:
        return None
    if isinstance(value, str):
        return value
    return str(value)


def check_records(
    records: Sequence[dict[str, Any]],
) -> tuple[list[CrossrefWork], list[RejectedRecord]]:
    """Разделяет записи на принятые и отклонённые."""
    accepted: list[CrossrefWork] = []
    rejected: list[RejectedRecord] = []

    for raw in records:
        try:
            accepted.append(CrossrefWork.model_validate(raw))
        except ValidationError as error:
            errors = error.errors()
            if errors:
                first = errors[0]
                location = ".".join(str(part) for part in first["loc"])
                reason = f"{location}: {first['msg']}"
            else:
                reason = "Ошибка проверки данных"

            rejected.append((_doi_for_log(raw.get("DOI")), reason))

    return accepted, rejected


def save_rejected(
    rejected: Sequence[RejectedRecord],
    path: str | Path,
) -> None:
    """Сохраняет журнал отклонений в CSV."""
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)

    with destination.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as file:
        writer = csv.writer(file)
        writer.writerow(["doi", "reason"])
        writer.writerows(rejected)


def to_publication(work: CrossrefWork) -> Publication:
    """Преобразует запись Crossref в объект Publication."""
    year: int | None = None

    if work.issued is not None and work.issued.date_parts:
        first_date = work.issued.date_parts[0]
        if first_date:
            year = first_date[0]

    authors: list[str] = []
    for author in work.author:
        parts = [
            part.strip() for part in (author.given, author.family) if part
        ]
        if parts:
            authors.append(" ".join(parts))

    issns = [
        normalized
        for value in work.ISSN
        if (normalized := normalize_issn(value)) is not None
    ]

    journal_title = work.container_title[0] if work.container_title else None

    return Publication(
        title=work.title[0],
        year=year,
        doi=normalize_doi(work.DOI),
        journal_title=journal_title,
        authors=authors,
        issns=issns,
    )


def to_publication_openalex(work: OpenAlexWork) -> Publication:
    """Преобразует запись OpenAlex в объект Publication."""
    source = work.primary_location.source if work.primary_location else None

    raw_issns: list[str] = []
    if source is not None and source.issn:
        raw_issns.extend(source.issn)
    if source is not None and source.issn_l:
        raw_issns.append(source.issn_l)

    issns: list[str] = []
    for value in raw_issns:
        normalized = normalize_issn(value)
        if normalized is not None and normalized not in issns:
            issns.append(normalized)

    return Publication(
        title=work.title or "",
        year=work.publication_year,
        doi=normalize_doi(work.doi),
        journal_title=source.display_name if source else None,
        authors=[],
        issns=issns,
    )
