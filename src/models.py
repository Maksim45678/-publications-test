"""Типы предметной области системы проверки научных публикаций."""

from dataclasses import dataclass, field
from enum import Enum


class Quartile(str, Enum):
    """Квартиль научного журнала."""

    Q1 = "Q1"
    Q2 = "Q2"
    Q3 = "Q3"
    Q4 = "Q4"


class Decision(str, Enum):
    """Решения по результатам проверки публикации."""

    ACCEPTED = "accepted"
    ACCEPT = "accepted"  # noqa: PIE796
    PASS = "accepted"  # noqa: PIE796
    REJECTED = "rejected"
    REJECT = "rejected"  # noqa: PIE796
    FAIL = "rejected"  # noqa: PIE796
    REVIEW = "review"
    MANUAL_REVIEW = "review"  # noqa: PIE796


@dataclass(slots=True)
class Journal:
    """Описание научного издания."""

    title: str = ""
    issn: str | None = None
    quartile: Quartile | None = None
    level: int | None = None
    affiliation: str | None = None
    issns: list[str] = field(default_factory=list)
    name: str | None = None

    def __post_init__(self) -> None:
        """Проверяет название журнала и список ISSN."""
        normalized_title = (
            self.title.strip() if isinstance(self.title, str) else ""
        )
        normalized_name = (
            self.name.strip() if isinstance(self.name, str) else ""
        )
        title = normalized_title or normalized_name

        if not title:
            raise ValueError("Название журнала не должно быть пустым")

        self.title = title
        self.name = title

        if not isinstance(self.issns, list) or any(
            not isinstance(value, str) for value in self.issns
        ):
            raise ValueError("Поле issns должно быть списком строк")

        if self.level is not None and (
            type(self.level) is not int or not 1 <= self.level <= 6
        ):
            raise ValueError(
                "Уровень журнала должен быть целым числом от 1 до 6"
            )


@dataclass(slots=True)
class Publication:
    """Научная публикация во внутреннем представлении."""

    title: str
    year: int | None = None
    doi: str | None = None
    journal_title: str | None = None
    authors: list[str] = field(default_factory=list)
    issns: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Проверяет ограничения полей перед созданием объекта."""
        if not isinstance(self.title, str) or not self.title.strip():
            raise ValueError("Название публикации не должно быть пустым")
        self.title = self.title.strip()

        if self.year is not None and (
            type(self.year) is not int or not 1900 <= self.year <= 2100
        ):
            raise ValueError("Год публикации должен быть от 1900 до 2100")

        if self.doi is not None and not isinstance(self.doi, str):
            raise ValueError("DOI должен быть строкой или None")

        if self.journal_title is not None and not isinstance(
            self.journal_title, str
        ):
            raise ValueError("Название журнала должно быть строкой или None")

        if not isinstance(self.authors, list) or any(
            not isinstance(author, str) for author in self.authors
        ):
            raise ValueError("Авторы должны быть списком строк")

        if not isinstance(self.issns, list) or any(
            not isinstance(issn, str) for issn in self.issns
        ):
            raise ValueError("ISSN должны быть списком строк")


@dataclass(slots=True)
class CheckResult:
    """Результат проверки публикации."""

    decision: Decision = Decision.REVIEW
    reasons: list[str] = field(default_factory=list)
    publication: Publication | None = None
    journal: Journal | None = None
    accepted: bool | None = None

    def __post_init__(self) -> None:
        """Проверяет причины решения и определяет признак принятия."""
        if not isinstance(self.reasons, list) or any(
            not isinstance(reason, str) for reason in self.reasons
        ):
            raise ValueError("Причины решения должны быть списком строк")

        if self.accepted is None:
            self.accepted = self.decision == Decision.ACCEPTED
