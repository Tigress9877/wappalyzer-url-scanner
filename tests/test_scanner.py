from __future__ import annotations

from typing import List

from src.wappalyzer_scanner.config import Config
from src.wappalyzer_scanner.scanner import Scanner
from src.wappalyzer_scanner.utils import Tech


class DummyClient:
    def __init__(self, *_: object, **__: object) -> None:
        pass
    def analyze(self, url: str) -> List[Tech]:  # pragma: no cover - simple mock
        if "bad" in url:
            raise RuntimeError("boom")
        return [Tech(name="Nginx", categories=["Web Servers"])]


def test_scanner_success(monkeypatch) -> None:
    cfg = Config()
    s = Scanner(cfg)
    # replace the real client with a dummy one
    monkeypatch.setattr(s, "client", DummyClient())

    recs = s.run(["https://ok.com"])
    assert recs[0].status == "success"
    assert recs[0].technologies[0].name == "Nginx"


def test_scanner_error(monkeypatch) -> None:
    cfg = Config()
    s = Scanner(cfg)
    monkeypatch.setattr(s, "client", DummyClient())

    recs = s.run(["https://bad.com"])
    assert recs[0].status == "error"
    assert recs[0].error
