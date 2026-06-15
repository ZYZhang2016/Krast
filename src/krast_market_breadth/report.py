"""Report rendering for market breadth analysis."""

from __future__ import annotations

from dataclasses import asdict
from typing import Any

from .analysis import AnalysisConfig
from .models import CandidateSectorResult, StockRow

DISCLAIMER = "Data analysis only. This report is not trading advice."


def analysis_to_dict(
    latest_date: str,
    config: AnalysisConfig,
    results: list[CandidateSectorResult],
) -> dict[str, Any]:
    return {
        "latest_date": latest_date,
        "config": config.to_dict(),
        "disclaimer": DISCLAIMER,
        "sectors": [_sector_to_dict(result) for result in results],
    }


def render_text_report(report: dict[str, Any]) -> str:
    lines = [
        "Market Breadth Weak-to-Strong Report",
        f"Latest date: {report['latest_date']}",
        f"{DISCLAIMER}",
        "",
    ]

    sectors = report.get("sectors", [])
    if not sectors:
        lines.append(f"No weak-to-strong candidates found for {report['latest_date']}.")
        return "\n".join(lines)

    lines.append("Stock codes marked with * closed above MA20.")
    lines.append("")

    for sector in sectors:
        evidence = sector["evidence"]
        lines.append(f"## {sector['sector']}")
        lines.append(
            "Signal: "
            f"latest={evidence['latest']:.2f}, "
            f"recent_avg={evidence['recent_avg']:.2f}, "
            f"comparison_avg={evidence['comparison_avg']:.2f}, "
            f"recent_low={evidence['recent_low']:.2f}, "
            f"rebound={evidence['rebound']:.2f}, "
            f"last_cross={evidence['last_cross_date'] or '-'}, "
            f"score={evidence['score']:.2f}"
        )

        if sector.get("error"):
            lines.append(f"Stocks: error: {sector['error']}")
            lines.append("")
            continue

        summary = sector["stock_summary"]
        lines.append(
            "Stocks: "
            f"{summary['count']} total, "
            f"{summary['above_ma20_count']} above MA20, "
            f"{summary['up_count']} up, "
            f"{summary['down_count']} down"
        )
        lines.append("Codes: " + _format_stocks(sector["stocks"]))
        lines.append("")

    return "\n".join(lines).rstrip()


def _sector_to_dict(result: CandidateSectorResult) -> dict[str, Any]:
    stock_result = result.stocks
    return {
        "sector": result.candidate.sector,
        "latest_date": result.candidate.latest_date,
        "evidence": asdict(result.candidate),
        "stock_summary": asdict(stock_result.summary),
        "stocks": [_stock_to_dict(stock) for stock in stock_result.stocks],
        "error": stock_result.error,
    }


def _stock_to_dict(stock: StockRow) -> dict[str, Any]:
    return {
        "code": stock.code,
        "name": stock.name,
        "industry": stock.industry,
        "date": stock.date,
        "close_price": stock.close_price,
        "ma20": stock.ma20,
        "change_percent": stock.change_percent,
        "above_ma20": stock.above_ma20,
    }


def _format_stocks(stocks: list[dict[str, Any]]) -> str:
    if not stocks:
        return "-"
    formatted = []
    for stock in stocks:
        marker = "*" if stock["above_ma20"] else ""
        name = f" {stock['name']}" if stock.get("name") else ""
        formatted.append(f"{stock['code']}{marker}{name}")
    return ", ".join(formatted)
