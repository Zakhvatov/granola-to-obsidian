# Changelog

All notable changes to this project are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.0] - 2026-11-08

### Added

- Import one Granola note into an Obsidian vault by its public share link.
- Automatic Obsidian vault detection, with `GRANOLA_VAULT` and `GRANOLA_FOLDER`
  overrides.
- Markdown frontmatter with `granola_id`, share URL, date and attendees.
- Duplicate protection and `--force` to overwrite.
- macOS Service (`Granola to Obsidian`) for a global keyboard shortcut.
- Tests with synthetic fixtures, Ruff and ShellCheck in CI.
