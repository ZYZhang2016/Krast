"""Weak-to-strong market breadth analysis."""

from __future__ import annotations

from dataclasses import asdict, dataclass

from .models import BreadthDataset, SectorEvidence, StockRow, StockSummary


@dataclass(frozen=True)
class AnalysisConfig:
    weak_threshold: float = 50.0
    strong_threshold: float = 50.0
    recent_window: int = 3
    comparison_window: int = 5
    lookback_window: int = 10
    min_rebound: float = 5.0
    min_improvement: float = 3.0
    max_sectors: int = 10
    include_confirmed_strong: bool = False

    def to_dict(self) -> dict[str, object]:
        return asdict(self)

    def validate(self) -> None:
        for field_name in ("recent_window", "comparison_window", "lookback_window", "max_sectors"):
            value = getattr(self, field_name)
            if value <= 0:
                raise ValueError(f"{field_name} must be greater than 0")
        if self.strong_threshold < self.weak_threshold:
            raise ValueError("strong_threshold must be greater than or equal to weak_threshold")


def analyze_breadth(dataset: BreadthDataset, config: AnalysisConfig) -> list[SectorEvidence]:
    config.validate()
    series_by_sector = build_sector_series(dataset)
    candidates: list[SectorEvidence] = []

    for sector, series in series_by_sector.items():
        evidence = _analyze_sector(dataset.dates, sector, series, config)
        if evidence:
            candidates.append(evidence)

    candidates.sort(key=lambda item: item.score, reverse=True)
    return candidates[: config.max_sectors]


def build_sector_series(dataset: BreadthDataset) -> dict[str, list[float | None]]:
    series = {industry: [None] * len(dataset.dates) for industry in dataset.industries}
    for date_index, industry_index, value in dataset.data:
        sector = dataset.industries[industry_index]
        series[sector][date_index] = value
    return series


def summarize_stocks(stocks: list[StockRow]) -> StockSummary:
    return StockSummary(
        count=len(stocks),
        above_ma20_count=sum(1 for stock in stocks if stock.above_ma20),
        up_count=sum(1 for stock in stocks if stock.change_percent is not None and stock.change_percent > 0),
        down_count=sum(1 for stock in stocks if stock.change_percent is not None and stock.change_percent < 0),
    )


def _analyze_sector(
    dates: list[str],
    sector: str,
    raw_series: list[float | None],
    config: AnalysisConfig,
) -> SectorEvidence | None:
    if len(raw_series) < config.recent_window + config.comparison_window:
        return None
    if raw_series[-1] is None:
        return None

    series = [float(value) if value is not None else None for value in raw_series]
    latest = series[-1]
    previous = _last_known(series[:-1])
    recent_values = _known_values(series[-config.recent_window :])
    comparison_start = max(0, len(series) - config.recent_window - config.comparison_window)
    comparison_end = len(series) - config.recent_window
    comparison_values = _known_values(series[comparison_start:comparison_end])
    prior_start = max(0, len(series) - config.lookback_window - 1)
    prior_values = _known_values(series[prior_start:-1])

    if latest is None or not recent_values or not comparison_values or not prior_values:
        return None

    recent_avg = _average(recent_values)
    comparison_avg = _average(comparison_values)
    improvement = recent_avg - comparison_avg
    recent_low = min(prior_values)
    rebound = latest - recent_low
    had_recent_weak = any(value < config.weak_threshold for value in prior_values)
    latest_is_strong = latest >= config.strong_threshold
    crossed_latest = previous is not None and previous < config.strong_threshold <= latest
    recent_avg_crossed = comparison_avg < config.strong_threshold <= recent_avg
    improving_enough = improvement >= config.min_improvement
    rebounded_enough = rebound >= config.min_rebound
    confirmed_strong = config.include_confirmed_strong and latest_is_strong and recent_avg >= config.strong_threshold

    if not latest_is_strong:
        return None
    if not ((had_recent_weak and improving_enough and rebounded_enough) or confirmed_strong):
        return None

    last_cross_date = _last_cross_date(dates, series, config.strong_threshold)
    recent_red_count = sum(1 for value in recent_values if value >= config.strong_threshold)
    prior_weak_count = sum(1 for value in prior_values if value < config.weak_threshold)
    score = (
        20.0
        + max(improvement, 0.0) * 1.2
        + max(rebound, 0.0) * 0.45
        + recent_red_count * 3.0
        + prior_weak_count * 1.2
        + (8.0 if crossed_latest or recent_avg_crossed or last_cross_date else 0.0)
    )

    return SectorEvidence(
        sector=sector,
        latest_date=dates[-1],
        latest=round(latest, 2),
        previous=round(previous, 2) if previous is not None else None,
        recent_avg=round(recent_avg, 2),
        comparison_avg=round(comparison_avg, 2),
        improvement=round(improvement, 2),
        recent_low=round(recent_low, 2),
        rebound=round(rebound, 2),
        last_cross_date=last_cross_date,
        recent_red_count=recent_red_count,
        prior_weak_count=prior_weak_count,
        score=round(score, 2),
    )


def _known_values(values: list[float | None]) -> list[float]:
    return [value for value in values if value is not None]


def _average(values: list[float]) -> float:
    return sum(values) / len(values)


def _last_known(values: list[float | None]) -> float | None:
    for value in reversed(values):
        if value is not None:
            return value
    return None


def _last_cross_date(dates: list[str], series: list[float | None], threshold: float) -> str | None:
    last_cross: str | None = None
    for index in range(1, len(series)):
        previous = series[index - 1]
        current = series[index]
        if previous is not None and current is not None and previous < threshold <= current:
            last_cross = dates[index]
    return last_cross
