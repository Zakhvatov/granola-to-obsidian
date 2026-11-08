# Contributing

Thanks for taking the time to contribute.

## Development setup

```bash
git clone https://github.com/Zakhvatov/granola-to-obsidian.git
cd granola-to-obsidian
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
```

## Checks

Run these before opening a pull request:

```bash
pytest
ruff check .
shellcheck install.sh
```

The same checks run in GitHub Actions.

## Pull requests

- Keep changes focused; one topic per pull request.
- Add or update tests for parser and filename changes.
- Update `CHANGELOG.md` for user-visible changes.
- Use synthetic fixtures only. Never commit a real meeting note, a real
  `notes.granola.ai` share link, an API token or a personal path.

## Reporting parser changes

Granola can change the share page format. If parsing breaks, include a
sanitized snippet of the page structure (no meeting content, names, tokens or
URLs) in the issue, or add a fixture that reproduces the new shape.
