from __future__ import annotations

import json
import logging
import threading
import time
from dataclasses import dataclass
from typing import List

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .config import Config
from .utils import Tech

logger = logging.getLogger(__name__)

API_BASE = "https://api.wappalyzer.com/v2/lookup/"


class RateLimiter:
    """Simple token-bucket rate limiter (thread-safe)."""

    def __init__(self, rate_per_sec: float, capacity: int | None = None) -> None:
        self.rate = float(max(rate_per_sec, 0.1))
        self.capacity = int(capacity or max(1, int(self.rate)))
        self.tokens = float(self.capacity)
        self.lock = threading.Lock()
        self.timestamp = time.monotonic()

    def acquire(self) -> None:
        with self.lock:
            now = time.monotonic()
            delta = now - self.timestamp
            self.timestamp = now
            self.tokens = min(self.capacity, self.tokens + delta * self.rate)
            if self.tokens < 1.0:
                sleep_for = (1.0 - self.tokens) / self.rate
                time.sleep(max(0.0, sleep_for))
                self.tokens = 0.0
            else:
                self.tokens -= 1.0


@dataclass
class APIOptions:
    api_key: str
    live: bool
    recursive: bool
    timeout: int
    verify_ssl: bool


class WappalyzerClient:
    """Unified client that prefers API and falls back to python library."""

    def __init__(self, cfg: Config) -> None:
        self.cfg = cfg
        self.session = requests.Session()
        retries = Retry(
            total=3,
            backoff_factor=0.5,
            status_forcelist=(429, 500, 502, 503, 504),
            allowed_methods=("GET",),
        )
        self.session.mount("https://", HTTPAdapter(max_retries=retries))
        self.session.mount("http://", HTTPAdapter(max_retries=retries))
        self.limiter = RateLimiter(cfg.rate_limit_rps, capacity=int(cfg.rate_limit_rps))

        self._method = self._select_method()
        logger.debug("Selected method: %s", self._method)

    def _select_method(self) -> str:
        if self.cfg.method == "api":
            return "api"
        if self.cfg.method == "python":
            return "python"
        return "api" if self.cfg.api_key else "python"

    # ------------- API -------------
    def _api_call(self, url: str) -> List[Tech]:
        if not self.cfg.api_key:
            raise RuntimeError("WAPPALYZER_API_KEY is not set")
        params = {"urls": url, "recursive": str(bool(self.cfg.recursive)).lower()}
        if self.cfg.live:
            params["live"] = "true"
        headers = {"x-api-key": self.cfg.api_key}

        self.limiter.acquire()
        try:
            resp = self.session.get(
                API_BASE, headers=headers, params=params,
                timeout=self.cfg.request_timeout_seconds, verify=self.cfg.verify_ssl
            )
        except requests.RequestException as exc:
            raise ConnectionError(str(exc)) from exc

        if resp.status_code != 200:
            raise RuntimeError(f"API HTTP {resp.status_code}: {resp.text[:200]}")

        try:
            data = resp.json()
        except json.JSONDecodeError as exc:
            raise RuntimeError("Invalid JSON response from API") from exc

        if not isinstance(data, list) or not data:
            raise RuntimeError("Unexpected API response structure")

        entry = data[0]
        if "errors" in entry and entry["errors"]:
            raise RuntimeError("; ".join(map(str, entry["errors"])))

        techs: List[Tech] = []
        for t in entry.get("technologies", []) or []:
            name = t.get("name")
            cats = [c.get("name") for c in (t.get("categories") or []) if c.get("name")]
            if name:
                techs.append(Tech(name=name, categories=cats))
        return techs

    # ------------- python fallback -------------
    def _python_call(self, url: str) -> List[Tech]:
        try:
            from Wappalyzer import Wappalyzer, WebPage  # type: ignore
        except Exception as exc:  # pragma: no cover - import failure
            raise RuntimeError("python-Wappalyzer not available") from exc

        try:
            page = WebPage.new_from_url(url, verify_ssl=self.cfg.verify_ssl, timeout=self.cfg.request_timeout_seconds)
            wapp = Wappalyzer.latest()
            detected = wapp.analyze_with_fingerprints(page)  # dict[name -> details]
            return [Tech(name=k, categories=list(set(d.get("categories", [])))) for k, d in detected.items()]
        except Exception as exc:  # pragma: no cover - network/timeouts
            raise ConnectionError(str(exc)) from exc

    # ------------- public -------------
    def analyze(self, url: str) -> List[Tech]:
        if self._method == "api":
            return self._api_call(url)
        return self._python_call(url)
