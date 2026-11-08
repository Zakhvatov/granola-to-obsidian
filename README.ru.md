# Granola to Obsidian

[English](README.md) | **Русский**

[![CI](https://github.com/Zakhvatov/granola-to-obsidian/actions/workflows/ci.yml/badge.svg)](https://github.com/Zakhvatov/granola-to-obsidian/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/)

Импорт **одной выбранной заметки Granola** в vault Obsidian по её публичной
share-ссылке. Без API-ключа, OAuth-приложения и платного тарифа Granola.

У Granola нет штатного способа сохранить одну заметку в Obsidian. Этот
инструмент делает именно это:

1. В Granola открой заметку и нажми **Share -> Copy link**.
2. Нажми горячую клавишу (или запусти `granola-import`).
3. В vault попадает только эта заметка, в виде Markdown.

Заметка читается со страницы, которую Granola отдаёт по share-ссылке. Ни
приложение Granola, ни его кэш, ни аккаунт не читаются.

## Возможности

- Одна заметка за раз, без массового синка.
- Работает на бесплатном тарифе Granola.
- Без API-ключей и учётных данных.
- Сохраняет название, дату, участников и конспект заметки.
- Во frontmatter пишутся `granola_id` и ссылка на заметку.
- Защита от дублей: повторный импорт той же заметки не создаёт второй файл.
- Опциональный macOS-сервис: весь сценарий — «Copy link -> горячая клавиша».
- Только стандартная библиотека Python; HTTP-запрос делает `curl`.

## Требования

- macOS (буфер обмена и сервис используют системные инструменты).
- Python 3.9+ (подойдёт системный).
- Obsidian с локальным vault.
- `curl` (входит в macOS).

## Установка

```bash
git clone https://github.com/Zakhvatov/granola-to-obsidian.git
cd granola-to-obsidian
./install.sh
```

Установщик копирует CLI в `~/.local/bin/granola-import` и создаёт сервис
`Granola to Obsidian` в `~/Library/Services`.

Один раз назначь горячую клавишу:

**Системные настройки -> Клавиатура -> «Сочетания клавиш…» -> Службы ->
Granola to Obsidian** и запиши комбинацию, например
`Control+Option+Command+G`.

## Использование

Из Granola:

1. `Share` / `...` -> **Copy link**.
2. Нажми свою горячую клавишу.

Или из терминала:

```bash
granola-import                    # взять ссылку из буфера обмена
granola-import https://notes.granola.ai/t/...   # явная ссылка
granola-import --force <link>     # перезаписать существующий импорт
```

Заметка сохраняется в `Granola/YYYY-MM-DD Название.md` внутри vault.

Если vault один или один открыт, скрипт найдёт его сам. Иначе укажи явно:

```bash
export GRANOLA_VAULT="$HOME/Documents/My Vault"
export GRANOLA_FOLDER="Meetings/Granola"
```

Или передай `--vault` / `--folder` в командной строке. Все опции:
`granola-import --help`.

## Что попадает в заметку

- Название, дата, участники и AI-конспект, которые Granola показывает на
  share-странице.
- Твои приватные заметки и транскрипт **не** входят в публичную share-страницу,
  поэтому не импортируются. Для транскрипта используй «Copy transcript» в Granola.

## Приватность и ограничения

- **Share-ссылка публичная.** Любой, у кого она есть, увидит то, что Granola
  показывает на странице. Не делись ссылками на чувствительные заметки.
- Инструмент делает ровно один запрос: на share-URL `notes.granola.ai`.
  Телеметрии нет, запись идёт только в локальный vault.
- Это неофициальный инструмент, не связанный с Granola. Формат share-страницы
  может измениться — тогда парсер сломается.
- Инструмент предназначен для твоих собственных заметок. Уважай условия
  Granola и приватность участников встреч.

## Разработка

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
pytest
ruff check .
shellcheck install.sh
```

Тесты используют только синтетические фикстуры; не коммить реальные записи
встреч, share-ссылки, токены и личные пути.

## Если что-то не работает

Логи: `~/.local/state/granola-import.log`.

Если сервис не появился в Системных настройках, запусти `./install.sh` ещё раз
и проверь, что `~/Library/Services/Granola to Obsidian.workflow` существует.

## Лицензия

MIT. См. [LICENSE](LICENSE).
