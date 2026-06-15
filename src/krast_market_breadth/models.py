"""Data models and validation helpers."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


class MarketBreadthValidationError(ValueError):
    """Raised when upstream payloads do not match the expected shape."""


@dataclass(frozen=True)
class BreadthDataset:
    dates: list[str]
    industries: list[str]
    data: list[tuple[int, int, float]]

    @property
    def latest_date(self) -> str:
        return self.dates[-1]


@dataclass(frozen=True)
class StockRow:
    code: str
    name: str
    industry: str
    date: str
    close_price: float | None = None
    ma20: float | None = None
    change_percent: float | None = None

    @property
    def above_ma20(self) -> bool:
        return self.close_price is not None and self.ma20 is not None and self.close_price > self.ma20


@dataclass(frozen=True)
class StockSummary:
    count: int = 0
    above_ma20_count: int = 0
    up_count: int = 0
    down_count: int = 0


@dataclass(frozen=True)
class StockFetchResult:
    sector: str
    date: str
    stocks: list[StockRow]
    summary: StockSummary = field(default_factory=StockSummary)
    error: str | None = None


@dataclass(frozen=True)
class SectorEvidence:
    sector: str
    latest_date: str
    latest: float
    previous: float | None
    recent_avg: float
    comparison_avg: float
    improvement: float
    recent_low: float
    rebound: float
    last_cross_date: str | None
    recent_red_count: int
    prior_weak_count: int
    score: float


@dataclass(frozen=True)
class CandidateSectorResult:
    candidate: SectorEvidence
    stocks: StockFetchResult


def parse_breadth_payload(payload: object) -> BreadthDataset:
    if not isinstance(payload, dict):
        raise MarketBreadthValidationError("market breadth response must be a JSON object")

    dates = _require_list(payload, "dates")
    industries = _require_list(payload, "industries")
    points = _require_list(payload, "data")

    if not dates:
        raise MarketBreadthValidationError("market breadth response field 'dates' is empty")
    if not industries:
        raise MarketBreadthValidationError("market breadth response field 'industries' is empty")

    parsed_dates = [str(item) for item in dates]
    parsed_industries = [str(item) for item in industries]
    parsed_points: list[tuple[int, int, float]] = []

    for index, point in enumerate(points):
        if not isinstance(point, (list, tuple)) or len(point) != 3:
            raise MarketBreadthValidationError(f"data point at index {index} must be [date_index, industry_index, value]")
        try:
            date_index = int(point[0])
            industry_index = int(point[1])
            value = float(point[2])
        except (TypeError, ValueError) as exc:
            raise MarketBreadthValidationError(f"data point at index {index} contains non-numeric indexes or value") from exc
        if not 0 <= date_index < len(parsed_dates):
            raise MarketBreadthValidationError(f"data point at index {index} has out-of-range date index {date_index}")
        if not 0 <= industry_index < len(parsed_industries):
            raise MarketBreadthValidationError(f"data point at index {index} has out-of-range industry index {industry_index}")
        parsed_points.append((date_index, industry_index, value))

    return BreadthDataset(dates=parsed_dates, industries=parsed_industries, data=parsed_points)


def parse_stock_payload(payload: object) -> list[StockRow]:
    if not isinstance(payload, dict):
        raise MarketBreadthValidationError("stock response must be a JSON object")
    rows = _require_list(payload, "data")

    stocks: list[StockRow] = []
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            raise MarketBreadthValidationError(f"stock row at index {index} must be an object")
        raw_code = row.get("stock_code")
        if raw_code is None:
            raise MarketBreadthValidationError(f"stock row at index {index} is missing stock_code")
        stocks.append(
            StockRow(
                code=normalize_stock_code(raw_code),
                name=str(row.get("stock_name") or ""),
                industry=str(row.get("industry") or payload.get("industry") or ""),
                date=str(row.get("date") or payload.get("date") or ""),
                close_price=_optional_float(row.get("close_price")),
                ma20=_optional_float(row.get("ma20")),
                change_percent=_optional_float(row.get("change_percent")),
            )
        )
    return stocks


def normalize_stock_code(value: object) -> str:
    text = str(value).strip()
    if text.endswith(".0"):
        text = text[:-2]
    if text.isdigit():
        return text.zfill(6)
    return text


def _require_list(payload: dict[str, Any], key: str) -> list[Any]:
    value = payload.get(key)
    if not isinstance(value, list):
        raise MarketBreadthValidationError(f"market breadth response missing required list field '{key}'")
    return value


def _optional_float(value: object) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None
