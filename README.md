# Система проверки публикаций кафедры

Проект выполняется в рамках дисциплины «Прикладное программирование
на языке высокого уровня» (РОСБИОТЕХ, кафедра АСУБП).

Автор: Шучков Максим Денисович 26o-090401-ИТ/2

## Запуск

```
Лабороторная 1
uv sync
uv run python main_lab1_backup.py
Лабороторная 2
uv run python main.py

```

## Проверка оформления кода

```
Лабороторна 1
grep -c '^name = ' uv.lock
uv sync --locked
uv run ruff check
uv run ruff format --check
Лабороторная 2
uv run python -m checks.pw2_check
uv run mypy src main.py
uv run ruff format --check
head -n 10 data/output/rejected.csv
doi,reason
```
