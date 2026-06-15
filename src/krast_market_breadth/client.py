"""HTTP client for the market breadth source."""

from __future__ import annotations

import json
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urljoin
from urllib.request import Request, urlopen


class DataFetchError(RuntimeError):
    """Raised when upstream data cannot be fetched."""


class MarketBreadthClient:
    def __init__(self, base_url: str = "https://sckd.dapanyuntu.com", timeout: float = 20.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def fetch_latest_breadth(self, page: int = 0) -> object:
        return self._get_json(
            "/api/api/industry_ma20_analysis_page",
            {"page": str(page)},
            referer=f"{self.base_url}/",
        )

    def fetch_sector_stocks(self, industry: str, date: str) -> object:
        return self._get_json(
            "/api/api/stock_daily_data_by_industry_and_date",
            {"industry": industry, "date": date},
            referer=f"{self.base_url}/industry_stocks.html",
        )

    def _get_json(self, path: str, params: dict[str, str], referer: str) -> object:
        query = urlencode(params)
        url = urljoin(f"{self.base_url}/", path.lstrip("/"))
        if query:
            url = f"{url}?{query}"
        request = Request(
            url,
            headers={
                "Accept": "application/json,text/plain,*/*",
                "Referer": referer,
                "User-Agent": (
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/125.0 Safari/537.36"
                ),
            },
        )
        try:
            with urlopen(request, timeout=self.timeout) as response:
                raw = response.read().decode("utf-8")
        except HTTPError as exc:
            raise DataFetchError(f"HTTP {exc.code} fetching {url}") from exc
        except URLError as exc:
            raise DataFetchError(f"network error fetching {url}: {exc.reason}") from exc

        try:
            return json.loads(raw)
        except json.JSONDecodeError as exc:
            raise DataFetchError(f"response from {url} was not valid JSON") from exc
