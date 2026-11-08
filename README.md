# Granola to Obsidian

Import **one selected Granola note** into an Obsidian vault from its public
share link. No API key, OAuth app, or paid Granola plan required.

Granola has no built-in Obsidian integration. The usual options are to sync all
notes (and get everything, wanted or not) or to copy them by hand. This tool
takes a different route:

1. In Granola, open a note and use **Share -> Copy link**.
2. Press a keyboard shortcut (or run `granola-import`).
3. Only that note is written to your vault as Markdown.

The note is taken from the page Granola serves for the share link. Nothing is
read from the Granola app, its cache, or your account.

## Features

- One note at a time, not a bulk sync.
- Works with the free Granola plan.
- No API keys or credentials.
- Preserves title, date, attendees and the note summary.
- Frontmatter includes `granola_id` and the share URL.
- Duplicate-safe: re-importing the same note does not create a second file.
- Optional macOS Service so the whole flow is "Copy link -> press shortcut".

## Requirements

- macOS (clipboard access and the optional Service use macOS tools).
- Python 3 (the system Python is enough).
- Obsidian with a local vault.
- `curl` (ships with macOS).

## Install

```bash
git clone https://github.com/Zakhvatov/granola-to-obsidian.git
cd granola-to-obsidian
./install.sh
```

The installer copies the CLI to `~/.local/bin/granola-import` and creates the
`Granola to Obsidian` Service in `~/Library/Services`.

Then assign a shortcut once:

**System Settings -> Keyboard -> Keyboard Shortcuts... -> Services ->
Granola to Obsidian** and record a combination, for example
`Control+Option+Command+G`.

## Usage

From Granola:

1. `Share` / `...` -> **Copy link**.
2. Press your shortcut.

Or from a terminal:

```bash
granola-import                    # read the link from the clipboard
granola-import https://notes.granola.ai/t/...   # explicit link
granola-import --force <link>     # overwrite an existing import
```

The note is written to `Granola/YYYY-MM-DD Title.md` inside the vault.

If there is exactly one Obsidian vault, or one vault open, the script finds it
automatically. Otherwise set it explicitly:

```bash
export GRANOLA_VAULT="$HOME/Documents/My Vault"
export GRANOLA_FOLDER="Meetings/Granola"
```

Or pass `--vault` / `--folder` on the command line.

## What gets imported

- The note title, date, attendees and the AI summary shown on the share page.
- Your private notes and the transcript are **not** part of the public share
  page, so they are not imported. Use Granola's "Copy transcript" for those.

## Privacy and limitations

- **The share link is public.** Anyone who has it can read what Granola shows on
  that page. Do not share links to sensitive notes.
- The tool sends exactly one request: the share URL, to `notes.granola.ai`.
  It has no telemetry and writes only to your local vault.
- This is an unofficial tool. It is not affiliated with Granola. The share page
  format may change; if it does, parsing can break.
- The tool is intended for your own notes. Respect Granola's terms and the
  privacy of meeting participants.

## Troubleshooting

Logs are written to `~/.local/state/granola-import.log`.

If the Service does not appear in System Settings, run `./install.sh` again and
check that `~/Library/Services/Granola to Obsidian.workflow` exists.

## License

MIT. See [LICENSE](LICENSE).
