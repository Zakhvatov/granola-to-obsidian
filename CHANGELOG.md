# Changelog

All notable changes to this project are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.1] - 2026-11-11

### Added

- `~/Applications/Granola to Obsidian.app` launcher with its own privacy
  identity. The Service now goes through it, so vault access no longer depends
  on which app was frontmost when the shortcut fired.

### Fixed

- Summary text stored behind Next.js flight references (`"original_content":
  "$6b"`) was written to the note verbatim instead of being resolved.
- A vault inside a macOS privacy-protected folder (`Documents`, `Desktop`,
  `Downloads`, iCloud Drive) no longer ends in a raw traceback: the folder is
  probed before the download, and the error names the app whose permission is
  missing and points at Full Disk Access.
- Nested lists keep their nesting, ordered lists get numbers, and body headings
  are demoted so the note keeps a single top level.

## [1.0.0] - 2026-11-08

### Added

- Import one Granola note into an Obsidian vault by its public share link.
- Automatic Obsidian vault detection, with `GRANOLA_VAULT` and `GRANOLA_FOLDER`
  overrides.
- Markdown frontmatter with `granola_id`, share URL, date and attendees.
- Duplicate protection and `--force` to overwrite.
- macOS Service (`Granola to Obsidian`) for a global keyboard shortcut.
- Tests with synthetic fixtures, Ruff and ShellCheck in CI.
