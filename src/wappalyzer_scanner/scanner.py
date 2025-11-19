from __future__ import annotations

import concurrent.futures as cf
import logging
from typing import Iterable, List

from .config import Config
from .utils import Record, Tech, normalize_url
from .wappalyzer_client import WappalyzerClient

logger = logging.getLogger(__name__)


class Scanner:
    """High-level orchestration: read -> analyze (concurrent) -> collect records."""

    def __init__(self, cfg: Config) -> None:
        self.cfg = cfg
        self.client = WappalyzerClient(cfg)

    def process_one(self, raw_url: str) -> Record:
        try:
            url = normalize_url(raw_url)
        except Exception as exc:  # invalid URL
            return Record(url=raw_url, status="error", error=str(exc), technologies=[])

        try:
            techs: List[Tech] = self.client.analyze(url)
            return Record(url=url, status="success", error=None, technologies=sorted(techs, key=lambda t: t.name.lower()))
        except Exception as exc:  # API/network/tool errors
            logger.warning("Failed to analyze %s: %s", url, exc)
            return Record(url=url, status="error", error=str(exc), technologies=[])

    def run(self, urls: Iterable[str]) -> List[Record]:
        results: List[Record] = []
        with cf.ThreadPoolExecutor(max_workers=self.cfg.max_workers) as ex:
            futs = [ex.submit(self.process_one, u) for u in urls]
            for fut in cf.as_completed(futs):
                results.append(fut.result())
        # preserve input order by stable map
        order = {u: i for i, u in enumerate(urls)}
        results.sort(key=lambda r: order.get(r.url, 10**9))
        return results
