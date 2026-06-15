from __future__ import annotations

import json
import unittest
from pathlib import Path

from krast_market_breadth.cli import main


FIXTURES = Path(__file__).parent / "fixtures"


class ReportCliTests(unittest.TestCase):
    def test_json_output_shape(self) -> None:
        from io import StringIO
        from unittest.mock import patch

        stdout = StringIO()
        with patch("sys.stdout", stdout):
            exit_code = main(
                [
                    "--breadth-file",
                    str(FIXTURES / "market_breadth.json"),
                    "--stocks-dir",
                    str(FIXTURES / "stocks"),
                    "--output",
                    "json",
                ]
            )
        self.assertEqual(exit_code, 0)
        payload = json.loads(stdout.getvalue())
        self.assertEqual(payload["latest_date"], "2026-06-15")
        self.assertIn("config", payload)
        self.assertGreaterEqual(len(payload["sectors"]), 1)
        self.assertIn("stocks", payload["sectors"][0])

    def test_no_candidates_text_output(self) -> None:
        from io import StringIO
        from unittest.mock import patch

        stdout = StringIO()
        with patch("sys.stdout", stdout):
            exit_code = main(
                [
                    "--breadth-file",
                    str(FIXTURES / "market_breadth.json"),
                    "--stocks-dir",
                    str(FIXTURES / "stocks"),
                    "--strong-threshold",
                    "99",
                ]
            )
        self.assertEqual(exit_code, 0)
        self.assertIn("No weak-to-strong candidates found", stdout.getvalue())

    def test_sector_stock_fetch_failure_is_reported(self) -> None:
        from io import StringIO
        from unittest.mock import patch

        stdout = StringIO()
        with patch("sys.stdout", stdout):
            exit_code = main(
                [
                    "--breadth-file",
                    str(FIXTURES / "market_breadth.json"),
                    "--stocks-dir",
                    str(FIXTURES / "stocks"),
                    "--max-sectors",
                    "10",
                    "--output",
                    "json",
                ]
            )
        self.assertEqual(exit_code, 0)
        payload = json.loads(stdout.getvalue())
        failures = [sector for sector in payload["sectors"] if sector["error"]]
        self.assertEqual(failures, [])

        missing_dir = FIXTURES / "missing-stocks"
        stdout = StringIO()
        with patch("sys.stdout", stdout):
            exit_code = main(
                [
                    "--breadth-file",
                    str(FIXTURES / "market_breadth.json"),
                    "--stocks-dir",
                    str(missing_dir),
                    "--output",
                    "json",
                ]
            )
        self.assertEqual(exit_code, 0)
        payload = json.loads(stdout.getvalue())
        self.assertTrue(any(sector["error"] for sector in payload["sectors"]))


if __name__ == "__main__":
    unittest.main()
