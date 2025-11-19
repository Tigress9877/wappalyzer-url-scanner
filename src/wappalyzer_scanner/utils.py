from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Iterable, List, Optional
from urllib.parse import urlparse


@dataclass
class Tech:
    name: str
    categories: List[str]


@dataclass
class Record:
    url: str
    status: str  # "success" | "error"
    error: Optional[str]
    technologies: List[Tech]


_SCHEME_RE = re.compile(r"^[a-zA-Z][a-zA-Z0-9+.-]*$")


def normalize_url(raw: str) -> str:
    """Normalize and validate a URL string.

    If scheme is missing, https:// is implicitly added.
    Raises ValueError on invalid input.
    """
    raw = (raw or "").strip()
    if not raw:
        raise ValueError("Empty URL line")

    parsed = urlparse(raw)
    if not parsed.scheme:
        raw = "https://" + raw
        parsed = urlparse(raw)

    if not _SCHEME_RE.match(parsed.scheme or ""):
        raise ValueError(f"Invalid URL scheme: {raw}")
    if not parsed.netloc:
        raise ValueError(f"Invalid URL host: {raw}")

    return raw


def ensure_dir(path: str | Path) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)


def format_txt(rec: Record) -> str:
    sep = "=" * 30
    if rec.status == "success":
        techs = "\n".join(
            f"- {t.name}" + (f" (categories: {', '.join(t.categories)})" if t.categories else "")
            for t in rec.technologies
        ) or "- (none)"
        err = ""
    else:
        techs = "- (none)"
        err = f"\nError: {rec.error}" if rec.error else ""
    return (
        f"{sep}\nURL: {rec.url}\nStatus: {rec.status.capitalize()}" + err + f"\nTechnologies:\n{techs}\n{sep}"
    )


def to_jsonl(rec: Record) -> str:
    return json.dumps(
        {
            "url": rec.url,
            "status": rec.status,
            "error": rec.error,
            "technologies": [
                {"name": t.name, "categories": t.categories} for t in rec.technologies
            ],
        },
        ensure_ascii=False,
    )


def setup_logging(level: str = "INFO") -> None:
    if logging.getLogger().handlers:
        return  # already configured
    lvl = getattr(logging, level.upper(), logging.INFO)
    root = logging.getLogger()
    root.setLevel(lvl)

    ch = logging.StreamHandler()
    ch.setLevel(lvl)
    ch.setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))

    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    fh = RotatingFileHandler(log_dir / "app.log", maxBytes=1_000_000, backupCount=3, encoding="utf-8")
    fh.setLevel(lvl)
    fh.setFormatter(
        logging.Formatter(fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
    )

    root.addHandler(ch)
    root.addHandler(fh)
