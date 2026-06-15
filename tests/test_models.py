from __future__ import annotations

import unittest

from krast_market_breadth.models import (
    MarketBreadthValidationError,
    normalize_stock_code,
    parse_breadth_payload,
    parse_stock_payload,
)


class ModelTests(unittest.TestCase):
    def test_parse_breadth_payload_requires_fields(self) -> None:
        with self.assertRaisesRegex(MarketBreadthValidationError, "dates"):
            parse_breadth_payload({"industries": [], "data": []})

    def test_parse_breadth_payload_rejects_malformed_point(self) -> None:
        payload = {"dates": ["2026-06-15"], "industries": ["银行"], "data": [["bad", 0, 10]]}
        with self.assertRaisesRegex(MarketBreadthValidationError, "non-numeric"):
            parse_breadth_payload(payload)

    def test_normalize_stock_code(self) -> None:
        self.assertEqual(normalize_stock_code(1.0), "000001")
        self.assertEqual(normalize_stock_code("23.0"), "000023")
        self.assertEqual(normalize_stock_code("601398"), "601398")

    def test_parse_stock_payload_normalizes_codes(self) -> None:
        stocks = parse_stock_payload(
            {
                "industry": "银行",
                "date": "2026-06-15",
                "data": [{"stock_code": 1.0, "stock_name": "平安银行", "close_price": 11, "ma20": 10}],
            }
        )
        self.assertEqual(stocks[0].code, "000001")
        self.assertTrue(stocks[0].above_ma20)


if __name__ == "__main__":
    unittest.main()
