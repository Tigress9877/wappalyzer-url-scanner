from __future__ import annotations

from pathlib import Path
from typing import List


def read_urls(path: str) -> List[str]:
    """Read lines from a file, strip blanks and comments, preserve order, deduplicate."""
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Input file not found: {p}")

    lines = p.read_text(encoding="utf-8", errors="ignore").splitlines()
    seen = set()
    out: List[str] = []
    for line in lines:
        s = (line or "").strip()
        if not s or s.startswith("#"):
            continue
        if s not in seen:
            out.append(s)
            seen.add(s)
    if not out:
        raise ValueError("Input file is empty or contains only comments")
    return out
