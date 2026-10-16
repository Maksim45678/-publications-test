# Система проверки публикаций кафедры

Проект выполняется в рамках дисциплины «Прикладное программирование
на языке высокого уровня» (РОСБИОТЕХ, кафедра АСУБП).

Автор: Шучков Максим Денисович 26o-090401-ИТ/2

## Запуск

```
uv sync
uv run python main.py

```

## Проверка оформления кода

```
uv run python -m checks.pw2_check
head -n 10 data/output/rejected.csv
uv run python main.py
uv run ruff check
uv run ruff format --check
```
