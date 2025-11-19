# src/wappalyzer_scanner/reader.py
from __future__ import annotations

import re
from pathlib import Path
from typing import List

# inline comments: one or more spaces, then a '#', then anything to end of line
_INLINE_COMMENT_RE = re.compile(r"\s+#.*$")

def read_urls(path: str) -> List[str]:
    """Read lines from a file, strip blanks and comments, preserve order, deduplicate.

    Rules:
    - Ignore empty lines.
    - Ignore full-line comments (lines starting with '#').
    - Strip *inline* comments that are preceded by whitespace, e.g. 'example.com  # note'.
      (This does NOT strip URL fragments like 'https://ex.com/#section' because there's no
       whitespace before '#'.)
    """
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
        # remove trailing inline comment if present
        s = _INLINE_COMMENT_RE.sub("", s).strip()
        if not s:
            continue
        if s not in seen:
            out.append(s)
            seen.add(s)
    if not out:
        raise ValueError("Input file is empty or contains only comments")
    return out
