from __future__ import annotations

import argparse
import logging
from pathlib import Path

from .config import Config
from .reader import read_urls
from .utils import Record, setup_logging
from .writer import write_records
from .scanner import Scanner


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="wappalyzer-url-scanner",
        description=(
            "Batch-detect web technologies using Wappalyzer (API preferred, python fallback). "
            "Outputs JSON Lines or TXT."
        ),
    )
    p.add_argument("--input", "-i", default=None, help="Path to input URLs file (default from env)")
    p.add_argument("--output", "-o", default=None, help="Path to output file (default from env)")
    p.add_argument("--format", "-f", choices=["jsonl", "txt"], default=None, help="Output format")

    p.add_argument("--method", choices=["api", "python", "auto"], default=None, help="Detection method")
    p.add_argument("--live", action="store_true", help="API: live=true (synchronous, shallow)")
    p.add_argument("--recursive", action="store_true", help="API: recursive=true (async crawl; not recommended)")

    p.add_argument("--max-workers", type=int, default=None, help="Thread pool size")
    p.add_argument("--timeout", type=int, default=None, help="HTTP timeout seconds")
    p.add_argument("--rate", type=float, default=None, help="API rate limit (requests/sec)")
    p.add_argument("--no-verify-ssl", action="store_true", help="Disable TLS verification (NOT recommended)")

    p.add_argument("--log-level", default=None, help="Logging level (INFO/DEBUG/WARN/ERROR)")
    p.add_argument("--verbose", "-v", action="store_true", help="Shortcut for --log-level DEBUG")

    return p


def main() -> int:
    parser = build_parser()
    ns = parser.parse_args()

    overrides = {
        "input_path": ns.input,
        "output_path": ns.output,
        "output_format": ns.format,
        "method": ns.method,
        "live": ns.live,
        "recursive": ns.recursive,
        "max_workers": ns.max_workers,
        "request_timeout_seconds": ns.timeout,
        "rate_limit_rps": ns.rate,
        "verify_ssl": not ns.no_verify_ssl if ns.no_verify_ssl is not None else None,
        "log_level": "DEBUG" if ns.verbose else ns.log_level,
    }

    cfg = Config.from_env(overrides=overrides)
    setup_logging(level=cfg.log_level)
    logging.getLogger(__name__).info("Starting scan | method=%s | fmt=%s", cfg.method, cfg.output_format)

    urls = read_urls(cfg.input_path)

    scanner = Scanner(cfg)
    records = scanner.run(urls)

    write_records(cfg.output_path, records, fmt=cfg.output_format)

    ok = sum(1 for r in records if r.status == "success")
    err = len(records) - ok
    print(
        f"Done. Results: {ok} success / {err} error / {len(records)} total\n"
        f"Saved to: {Path(cfg.output_path).resolve()}"
    )
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
