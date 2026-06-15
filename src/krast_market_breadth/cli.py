"""Command line interface for market breadth weak-to-strong analysis."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from urllib.parse import quote

from .analysis import AnalysisConfig, analyze_breadth, summarize_stocks
from .client import DataFetchError, MarketBreadthClient
from .models import (
    CandidateSectorResult,
    MarketBreadthValidationError,
    StockFetchResult,
    parse_breadth_payload,
    parse_stock_payload,
)
from .report import analysis_to_dict, render_text_report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="krast-weak-to-strong",
        description="Analyze A-share market breadth data and report weak-to-strong sector stock codes.",
    )
    parser.add_argument("--base-url", default="https://sckd.dapanyuntu.com", help="Market breadth site base URL.")
    parser.add_argument("--page", type=int, default=0, help="Market breadth page number. Page 0 is latest.")
    parser.add_argument("--timeout", type=float, default=20.0, help="HTTP timeout in seconds.")
    parser.add_argument("--output", choices=["text", "json"], default="text", help="Output format.")
    parser.add_argument("--breadth-file", type=Path, help="Read market breadth JSON from a local fixture file.")
    parser.add_argument("--stocks-dir", type=Path, help="Read sector stock JSON fixtures from this directory.")
    parser.add_argument("--strong-threshold", type=float, default=50.0, help="Breadth value treated as strong/red.")
    parser.add_argument("--weak-threshold", type=float, default=50.0, help="Breadth value treated as weak/green.")
    parser.add_argument("--recent-window", type=int, default=3, help="Recent trading-day window size.")
    parser.add_argument("--comparison-window", type=int, default=5, help="Prior comparison window size.")
    parser.add_argument("--lookback-window", type=int, default=10, help="Recent weakness lookback window size.")
    parser.add_argument("--min-rebound", type=float, default=5.0, help="Minimum rebound from recent low.")
    parser.add_argument("--min-improvement", type=float, default=3.0, help="Minimum recent-vs-prior average improvement.")
    parser.add_argument("--max-sectors", type=int, default=10, help="Maximum candidate sectors to report.")
    parser.add_argument(
        "--include-confirmed-strong",
        action="store_true",
        help="Allow sectors that are strong without recent weakness when they are improving.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    config = AnalysisConfig(
        weak_threshold=args.weak_threshold,
        strong_threshold=args.strong_threshold,
        recent_window=args.recent_window,
        comparison_window=args.comparison_window,
        lookback_window=args.lookback_window,
        min_rebound=args.min_rebound,
        min_improvement=args.min_improvement,
        max_sectors=args.max_sectors,
        include_confirmed_strong=args.include_confirmed_strong,
    )

    try:
        payload = _load_breadth_payload(args)
        dataset = parse_breadth_payload(payload)
        candidates = analyze_breadth(dataset, config)
        sector_results = [_load_sector_result(args, candidate.sector, dataset.latest_date) for candidate in candidates]
    except (DataFetchError, MarketBreadthValidationError, OSError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    results = [
        CandidateSectorResult(candidate=candidate, stocks=stocks)
        for candidate, stocks in zip(candidates, sector_results)
    ]
    report = analysis_to_dict(dataset.latest_date, config, results)

    if args.output == "json":
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(render_text_report(report))

    return 0


def _load_breadth_payload(args: argparse.Namespace) -> object:
    if args.breadth_file:
        return json.loads(args.breadth_file.read_text(encoding="utf-8"))

    client = MarketBreadthClient(base_url=args.base_url, timeout=args.timeout)
    return client.fetch_latest_breadth(page=args.page)


def _load_sector_result(args: argparse.Namespace, sector: str, date: str) -> StockFetchResult:
    try:
        if args.stocks_dir:
            payload = json.loads(_stock_fixture_path(args.stocks_dir, sector).read_text(encoding="utf-8"))
        else:
            client = MarketBreadthClient(base_url=args.base_url, timeout=args.timeout)
            payload = client.fetch_sector_stocks(sector, date)
        stocks = parse_stock_payload(payload)
        return StockFetchResult(sector=sector, date=date, stocks=stocks, summary=summarize_stocks(stocks))
    except (DataFetchError, MarketBreadthValidationError, OSError, json.JSONDecodeError, ValueError) as exc:
        return StockFetchResult(sector=sector, date=date, stocks=[], error=str(exc))


def _stock_fixture_path(stocks_dir: Path, sector: str) -> Path:
    candidates = [
        stocks_dir / f"{sector}.json",
        stocks_dir / f"{quote(sector, safe='')}.json",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return candidates[0]


if __name__ == "__main__":
    raise SystemExit(main())
