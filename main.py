"""Проверка и обработка учебных записей научных публикаций."""

import argparse
import json
from pathlib import Path

from src.loaders import (
    OpenAlexWork,
    check_records,
    load_items,
    save_rejected,
    to_publication,
    to_publication_openalex,
)
from src.models import Publication
from src.normalize import normalize_doi


def main() -> None:
    """Выполняет входной контроль и сохраняет журнал отклонений."""
    parser = argparse.ArgumentParser(
        description="Входной контроль метаданных публикаций"
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("data/raw/crossref_sample.json"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/output/rejected.csv"),
    )
    parser.add_argument(
        "--openalex-json",
        type=Path,
        default=None,
    )
    args = parser.parse_args()

    items = load_items(args.input)
    crossref_works, rejected = check_records(items)

    publications: list[Publication] = []
    conversion_errors = 0

    for work in crossref_works:
        try:
            publication = to_publication(work)
            publications.append(publication)
        except ValueError as error:
            rejected.append((normalize_doi(work.DOI), f"Publication: {error}"))
            conversion_errors += 1

    save_rejected(rejected, args.output)

    print(
        f"Crossref: Принято: {len(crossref_works)}, "
        f"отклонено: {len(items) - len(crossref_works)}"
    )
    print(
        f"Публикации: Принято: {len(publications)}, отклонено: {len(rejected)}"
    )
    print(f"Ошибок преобразования Publication: {conversion_errors}")
    print(f"Журнал отклонений: {args.output}")
    print(f"Источник данных: {args.input}")

    if args.openalex_json is not None:
        with args.openalex_json.open(
            "r",
            encoding="utf-8",
        ) as file:
            openalex_payload = json.load(file)

        openalex_work = OpenAlexWork.model_validate(openalex_payload)
        publication = to_publication_openalex(openalex_work)

        print(
            f"OpenAlex: DOI={publication.doi}, "
            f"год={publication.year}, ISSN={publication.issns}"
        )


if __name__ == "__main__":
    main()
