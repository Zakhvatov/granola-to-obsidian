import importlib.util
import json
import pathlib
from importlib.machinery import SourceFileLoader

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
LOADER = SourceFileLoader("granola_import", str(ROOT / "bin" / "granola-import"))
SPEC = importlib.util.spec_from_loader("granola_import", LOADER)
assert SPEC is not None
granola_import = importlib.util.module_from_spec(SPEC)
LOADER.exec_module(granola_import)


def make_page(panel=None):
    panel = panel or {
        "document": {
            "id": "11111111-1111-4111-8111-111111111111",
            "title": "Weekly planning",
            "created_at": "2026-11-07T22:34:40.457Z",
        },
        "panel": {
            "title": "Summary",
            "original_content": (
                "<h2>Decisions</h2><p>Ship <strong>it</strong> on Friday.</p>"
                "<ul><li>Alice writes the RFC</li><li>Bob reviews it</li></ul>"
                "<hr><p>See <a href=\"https://example.com\">the doc</a>.</p>"
            ),
        },
        "documentMetadata": {
            "attendees": [{"name": "Alice"}, {"name": "Bob"}],
        },
    }
    inner = '{"documentPanel":' + json.dumps(panel) + ',"other":true}'
    body = json.dumps(inner)[1:-1]
    return (
        "<html><head><title>Weekly planning</title></head><body>"
        f'<script>self.__next_f.push([1,"{body}"])</script>'
        "</body></html>"
    )


def test_find_url():
    url = "https://notes.granola.ai/t/11111111-1111-4111-8111-111111111111-test-token"
    assert granola_import.find_url(f"link: {url} text") == url
    assert granola_import.find_url("no link here") is None


def test_extract_payload():
    page = make_page()
    data = granola_import.extract_payload(page)
    assert '"documentPanel"' in data
    assert "Weekly planning" in data


def test_parse_note():
    url = "https://notes.granola.ai/t/11111111-1111-4111-8111-111111111111-test-token"
    note = granola_import.parse_note(make_page(), url)
    assert note["id"] == "11111111-1111-4111-8111-111111111111"
    assert note["title"] == "Weekly planning"
    assert note["attendees"] == ["Alice", "Bob"]
    assert "Ship <strong>it</strong>" in note["html"]
    assert note["url"] == url


def test_parse_note_falls_back_to_page_title():
    panel = {
        "document": {"id": "abc", "title": "", "created_at": "2026-11-07T22:34:40Z"},
        "panel": {"original_content": "<p>Hello</p>"},
        "documentMetadata": {},
    }
    note = granola_import.parse_note(make_page(panel), "https://notes.granola.ai/t/abc")
    assert note["title"] == "Weekly planning"


def test_html_to_markdown():
    markdown = granola_import.html_to_markdown(
        "<h2>Decisions</h2><p>Ship <strong>it</strong>.</p>"
        "<ul><li>One</li><li>Two</li></ul><hr>"
        '<p><a href="https://example.com">doc</a> &amp; notes</p>'
    )
    assert "## Decisions" in markdown
    assert "Ship **it**." in markdown
    assert "- One" in markdown
    assert "[doc](https://example.com)" in markdown
    assert "& notes" in markdown


def test_prosemirror_to_html():
    node = {
        "type": "doc",
        "content": [
            {"type": "heading", "attrs": {"level": 2}, "content": [{"type": "text", "text": "Plan"}]},
            {
                "type": "paragraph",
                "content": [
                    {"type": "text", "text": "Ship ", "marks": [{"type": "bold"}]},
                    {"type": "text", "text": "it"},
                ],
            },
        ],
    }
    result = granola_import.prosemirror_to_html(node)
    assert "<h2>Plan</h2>" in result
    assert "<strong>Ship </strong>" in result


def test_html_to_markdown_keeps_nested_lists():
    markdown = granola_import.html_to_markdown(
        "<ul><li>Outer<ul><li>Inner</li></ul></li><li>Second</li></ul>"
    )
    assert "- Outer" in markdown
    assert "\n  - Inner" in markdown
    assert "\n- Second" in markdown


def test_html_to_markdown_numbers_ordered_list():
    markdown = granola_import.html_to_markdown("<ol><li>One</li><li>Two</li></ol>")
    assert "1. One" in markdown
    assert "2. Two" in markdown


def test_demote_headings():
    assert granola_import.demote_headings("# A\n\ntext\n\n## B") == "## A\n\ntext\n\n### B"
    assert granola_import.demote_headings("## A\n### B") == "## A\n### B"


def test_build_markdown_demotes_body_headings():
    note = {
        "id": "abc",
        "title": "T",
        "created": "2026-11-07T22:34:40Z",
        "attendees": [],
        "html": "<h1>Decisions</h1><p>Ship it</p>",
        "url": "https://notes.granola.ai/t/abc",
    }
    markdown = granola_import.build_markdown(note)
    assert "\n## Decisions\n" in markdown


def test_sanitize_filename():
    assert granola_import.sanitize_filename('a/b:c*?"<>|d') == "a-b-c-d"
    assert granola_import.sanitize_filename("   ") == "Granola note"
    assert len(granola_import.sanitize_filename("x" * 200)) == 90


def test_local_date():
    assert granola_import.local_date("2026-11-07T22:34:40Z")[:4] == "2026"


def test_build_markdown():
    note = {
        "id": "abc",
        "title": 'Title with "quotes"',
        "created": "2026-11-07T22:34:40Z",
        "attendees": ["Alice", "Bob"],
        "html": "<p>Hello</p>",
        "url": "https://notes.granola.ai/t/abc",
    }
    markdown = granola_import.build_markdown(note)
    assert "granola_id: abc" in markdown
    assert 'title: "Title with \\"quotes\\""' in markdown
    assert "  - \"[[Alice]]\"" in markdown
    assert "## Summary" in markdown
    assert "Hello" in markdown


def make_page_with_chunk(panel, chunk_id, text):
    rows = [
        f"{chunk_id}:T{len(text.encode('utf-8')):x},{text}\n",
        '{"documentPanel":' + json.dumps(panel) + ',"other":true}',
    ]
    scripts = "".join(
        f'<script>self.__next_f.push([1,"{json.dumps(row)[1:-1]}"])</script>' for row in rows
    )
    return (
        "<html><head><title>Weekly planning</title></head><body>"
        f"{scripts}</body></html>"
    )


def test_parse_note_resolves_out_of_line_flight_text():
    panel = {
        "document": {
            "id": "abc",
            "title": "Weekly planning",
            "created_at": "2026-11-07T22:34:40Z",
        },
        "panel": {"original_content": "$6b", "generated_lines": []},
        "documentMetadata": {"attendees": []},
    }
    body = "<h1>Концепция</h1><ul><li>Цель: AI-ассистент</li></ul>"
    note = granola_import.parse_note(
        make_page_with_chunk(panel, "6b", body), "https://notes.granola.ai/t/abc"
    )
    assert note["html"] == body


def test_flight_text_chunks_counts_bytes_not_characters():
    text = "Концепция"  # 16 bytes in UTF-8, but only 8 characters
    payload = f"5d:T{len(text.encode('utf-8')):x},{text}\nnext row"
    assert granola_import.flight_text_chunks(payload) == {"5d": text}


def test_resolve_flight_refs():
    chunks = {"6b": "<p>Hi</p>"}
    value = {"original_content": "$6b", "keep": "$missing", "nested": ["$6b", 1]}
    assert granola_import.resolve_flight_refs(value, chunks) == {
        "original_content": "<p>Hi</p>",
        "keep": "$missing",
        "nested": ["<p>Hi</p>", 1],
    }


def test_parse_note_falls_back_to_generated_lines():
    panel = {
        "document": {"id": "abc", "title": "T", "created_at": "2026-11-07T22:34:40Z"},
        "panel": {"generated_lines": [{"text": "One"}, {"text": "Two"}]},
        "documentMetadata": {},
    }
    note = granola_import.parse_note(make_page(panel), "https://notes.granola.ai/t/abc")
    assert "<p>One</p>" in note["html"]
    assert "<p>Two</p>" in note["html"]


def test_already_imported(tmp_path):
    note_id = "abc"
    (tmp_path / "note.md").write_text(f"---\ngranola_id: {note_id}\n---\n", encoding="utf-8")
    assert granola_import.already_imported(tmp_path, note_id) == str(tmp_path / "note.md")
    assert granola_import.already_imported(tmp_path, "missing") is None


def test_already_imported_propagates_permission_error(tmp_path, monkeypatch):
    def denied(path):
        raise PermissionError(1, "Operation not permitted", str(path))

    monkeypatch.setattr(granola_import.os, "listdir", denied)
    with pytest.raises(PermissionError):
        granola_import.already_imported(tmp_path, "abc")


def test_protected_folder(tmp_path, monkeypatch):
    monkeypatch.setattr(granola_import.sys, "platform", "darwin")
    monkeypatch.setenv("HOME", str(tmp_path))
    assert granola_import.protected_folder(tmp_path / "Documents" / "Vault") == "Documents"
    assert granola_import.protected_folder(tmp_path / "Desktop") == "Desktop"
    assert (
        granola_import.protected_folder(tmp_path / "Library" / "Mobile Documents" / "Obsidian")
        == "iCloud Drive"
    )
    assert granola_import.protected_folder(tmp_path / "Projects" / "Vault") is None


def test_vault_error_points_to_full_disk_access(tmp_path, monkeypatch):
    monkeypatch.setattr(granola_import.sys, "platform", "darwin")
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setattr(granola_import, "caller_app", lambda: "Automator")
    message = granola_import.vault_error(
        PermissionError(1, "Operation not permitted"), tmp_path / "Documents" / "Vault"
    )
    assert "Automator" in message
    assert "Documents" in message
    assert "Full Disk Access" in message


def test_vault_error_keeps_other_errors_short(tmp_path):
    message = granola_import.vault_error(FileNotFoundError(2, "No such file"), tmp_path / "Vault")
    assert "Full Disk Access" not in message
    assert "cannot use" in message


def test_check_vault_dies_instead_of_crashing(tmp_path, monkeypatch, capsys):
    def denied(path):
        raise PermissionError(1, "Operation not permitted", str(path))

    home = tmp_path / "home"
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.setenv("GRANOLA_NO_NOTIFY", "1")
    monkeypatch.setattr(granola_import.sys, "platform", "darwin")
    monkeypatch.setattr(granola_import, "caller_app", lambda: "Automator")
    monkeypatch.setattr(granola_import, "open_privacy_settings", lambda: None)
    monkeypatch.setattr(granola_import, "LOG", str(tmp_path / "import.log"))
    monkeypatch.setattr(granola_import.os, "listdir", denied)

    with pytest.raises(SystemExit):
        granola_import.check_vault(home / "Documents" / "Vault")

    err = capsys.readouterr().err
    assert "Automator" in err
    assert "Full Disk Access" in err
    assert "Traceback" not in err


def test_die_vault_error_opens_settings_only_for_protected_folder(tmp_path, monkeypatch):
    calls = []
    monkeypatch.setenv("HOME", str(tmp_path / "home"))
    monkeypatch.setenv("GRANOLA_NO_NOTIFY", "1")
    monkeypatch.setattr(granola_import.sys, "platform", "darwin")
    monkeypatch.setattr(granola_import, "open_privacy_settings", lambda: calls.append(1))
    monkeypatch.setattr(granola_import, "LOG", str(tmp_path / "import.log"))

    with pytest.raises(SystemExit):
        granola_import.die_vault_error(
            PermissionError(1, "Operation not permitted"), tmp_path / "home" / "Documents" / "Vault"
        )
    with pytest.raises(SystemExit):
        granola_import.die_vault_error(
            PermissionError(1, "Operation not permitted"), tmp_path / "Projects" / "Vault"
        )

    assert len(calls) == 1


def test_version():
    assert granola_import.__version__ == "1.0.1"
