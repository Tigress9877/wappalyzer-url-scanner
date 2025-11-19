from __future__ import annotations

from pathlib import Path
from typing import Iterable

from .utils import Record, ensure_dir, format_txt, to_jsonl


def write_records(path: str, records: Iterable[Record], fmt: str = "jsonl") -> None:
    """Write records to a file in the requested format (jsonl|txt)."""
    ensure_dir(path)
    p = Path(path)
    if fmt == "jsonl":
        p.write_text("\n".join(to_jsonl(r) for r in records) + "\n", encoding="utf-8")
    elif fmt == "txt":
        p.write_text("\n".join(format_txt(r) for r in records) + "\n", encoding="utf-8")
    else:
        raise ValueError("Unsupported output format; use 'jsonl' or 'txt'")
