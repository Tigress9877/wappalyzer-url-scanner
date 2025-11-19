from __future__ import annotations

from pathlib import Path

from src.wappalyzer_scanner.utils import Record, Tech
from src.wappalyzer_scanner.writer import write_records


def test_write_jsonl(tmp_path: Path) -> None:
    recs = [
        Record(url="https://ex.com", status="success", error=None, technologies=[Tech("A", ["X"])]),
        Record(url="https://bad.com", status="error", error="timeout", technologies=[]),
    ]
    out = tmp_path / "out.jsonl"
    write_records(str(out), recs, fmt="jsonl")
    data = out.read_text(encoding="utf-8").strip().splitlines()
    assert len(data) == 2
    assert '"url": "https://ex.com"' in data[0]
    assert '"status": "error"' in data[1]


def test_write_txt(tmp_path: Path) -> None:
    recs = [Record(url="https://ex.com", status="success", error=None, technologies=[Tech("A", [])])]
    out = tmp_path / "out.txt"
    write_records(str(out), recs, fmt="txt")
    text = out.read_text(encoding="utf-8")
    assert "URL: https://ex.com" in text
    assert "Technologies:" in text
