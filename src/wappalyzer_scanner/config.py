from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional

from dotenv import load_dotenv


@dataclass
class Config:
    """Application configuration loaded from env vars and CLI overrides."""

    input_path: str = "data/URL.txt"
    output_path: str = "data/Result.txt"
    output_format: str = "jsonl"  # jsonl | txt

    method: str = "auto"  # api | python | auto

    # API
    api_key: Optional[str] = None
    live: bool = False
    recursive: bool = False
    rate_limit_rps: float = 5.0

    # runtime
    request_timeout_seconds: int = 20
    max_workers: int = 4
    verify_ssl: bool = True
    log_level: str = "INFO"

    @classmethod
    def from_env(cls, *, overrides: Optional[dict] = None) -> "Config":
        load_dotenv(override=False)
        cfg = cls()

        # strings
        cfg.input_path = os.getenv("INPUT_PATH", cfg.input_path)
        cfg.output_path = os.getenv("OUTPUT_PATH", cfg.output_path)
        cfg.output_format = os.getenv("OUTPUT_FORMAT", cfg.output_format)
        cfg.method = os.getenv("WAPPALYZER_METHOD", cfg.method).lower()
        cfg.api_key = os.getenv("WAPPALYZER_API_KEY")
        cfg.log_level = os.getenv("LOG_LEVEL", cfg.log_level).upper()

        # bool/int/float
        cfg.live = os.getenv("WAPPALYZER_LIVE", "false").lower() == "true"
        cfg.recursive = os.getenv("WAPPALYZER_RECURSIVE", "false").lower() == "true"
        cfg.request_timeout_seconds = int(os.getenv("REQUEST_TIMEOUT_SECONDS", cfg.request_timeout_seconds))
        cfg.max_workers = int(os.getenv("MAX_WORKERS", cfg.max_workers))
        cfg.verify_ssl = os.getenv("VERIFY_SSL", "true").lower() == "true"
        cfg.rate_limit_rps = float(os.getenv("RATE_LIMIT_RPS", cfg.rate_limit_rps))

        overrides = overrides or {}
        for k, v in overrides.items():
            if v is not None:
                setattr(cfg, k, v)

        if cfg.method not in {"api", "python", "auto"}:
            cfg.method = "auto"

        return cfg
