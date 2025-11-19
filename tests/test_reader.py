from __future__ import annotations

from pathlib import Path

from src.wappalyzer_scanner.reader import read_urls


def test_read_urls_basic(tmp_path: Path) -> None:
    p = tmp_path / "in.txt"
    p.write_text("""
# comment
example.com
https://python.org
example.com  # dup
""".strip(), encoding="utf-8")
    urls = read_urls(str(p))
    assert urls == ["example.com", "https://python.org"]


def test_read_urls_missing(tmp_path: Path) -> None:
    p = tmp_path / "missing.txt"
    try:
        read_urls(str(p))
    except FileNotFoundError:
        pass
    else:
        assert False, "Expected FileNotFoundError"


def test_read_urls_empty(tmp_path: Path) -> None:
    p = tmp_path / "empty.txt"
    p.write_text("# only comments", encoding="utf-8")
    try:
        read_urls(str(p))
    except ValueError as exc:
        assert "empty" in str(exc).lower()
    else:
        assert False, "Expected ValueError for empty file"
