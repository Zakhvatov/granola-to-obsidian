import importlib.util
import json
import pathlib
from importlib.machinery import SourceFileLoader

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


def test_already_imported(tmp_path):
    note_id = "abc"
    (tmp_path / "note.md").write_text(f"---\ngranola_id: {note_id}\n---\n", encoding="utf-8")
    assert granola_import.already_imported(tmp_path, note_id) == str(tmp_path / "note.md")
    assert granola_import.already_imported(tmp_path, "missing") is None


def test_version():
    assert granola_import.__version__ == "1.0.0"
