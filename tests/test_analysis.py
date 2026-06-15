from __future__ import annotations

import json
import unittest
from pathlib import Path

from krast_market_breadth.analysis import AnalysisConfig, analyze_breadth, build_sector_series, summarize_stocks
from krast_market_breadth.models import parse_breadth_payload, parse_stock_payload


FIXTURES = Path(__file__).parent / "fixtures"


class AnalysisTests(unittest.TestCase):
    def setUp(self) -> None:
        payload = json.loads((FIXTURES / "market_breadth.json").read_text(encoding="utf-8"))
        self.dataset = parse_breadth_payload(payload)

    def test_build_sector_series(self) -> None:
        series = build_sector_series(self.dataset)
        self.assertEqual(series["银行"][0], 25)
        self.assertEqual(series["今日翻红"][-1], 55)

    def test_detects_crossing_and_excludes_non_candidates(self) -> None:
        candidates = analyze_breadth(self.dataset, AnalysisConfig(max_sectors=10))
        names = {candidate.sector for candidate in candidates}
        self.assertIn("银行", names)
        self.assertIn("今日翻红", names)
        self.assertNotIn("持续强势", names)
        self.assertNotIn("仍然偏弱", names)

    def test_improving_but_still_weak_is_excluded(self) -> None:
        candidates = analyze_breadth(self.dataset, AnalysisConfig(max_sectors=10))
        self.assertTrue(all(candidate.sector != "仍然偏弱" for candidate in candidates))

    def test_summarize_stocks(self) -> None:
        payload = json.loads((FIXTURES / "stocks" / "银行.json").read_text(encoding="utf-8"))
        summary = summarize_stocks(parse_stock_payload(payload))
        self.assertEqual(summary.count, 3)
        self.assertEqual(summary.above_ma20_count, 2)
        self.assertEqual(summary.up_count, 1)
        self.assertEqual(summary.down_count, 1)


if __name__ == "__main__":
    unittest.main()
