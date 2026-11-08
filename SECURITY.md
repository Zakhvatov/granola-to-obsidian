# Security policy

## Reporting a vulnerability

Please report security issues privately through
[GitHub Security Advisories](https://github.com/Zakhvatov/granola-to-obsidian/security/advisories/new)
rather than in a public issue.

Do not include real meeting content, `notes.granola.ai` share links, tokens or
personal paths in a report. A minimal reproduction with synthetic data is
enough.

## Scope

This project has no server component and no telemetry. It downloads one public
Granola share page and writes a Markdown file to a local Obsidian vault.

Known limitations:

- A Granola share link is public by design. Anyone who has the link can read
  what Granola renders on that page.
- The parser depends on Granola's share page format and may break when that
  format changes.
- The tool does not read the Granola desktop app, its cache or your account.
