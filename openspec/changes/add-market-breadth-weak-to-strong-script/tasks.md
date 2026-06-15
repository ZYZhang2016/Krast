## 1. Project Setup

- [x] 1.1 Add Python project metadata and runtime dependency declarations for the CLI script.
- [x] 1.2 Create the `src/krast_market_breadth/` package structure with modules for CLI, client, models, analysis, and reporting.
- [x] 1.3 Add a command entry point for running the weak-to-strong analysis from the terminal.
- [x] 1.4 Add a short README section or usage document describing how to run the script and interpret the output.

## 2. Data Retrieval

- [x] 2.1 Implement an HTTP client for fetching the latest market breadth page data with browser-like headers.
- [x] 2.2 Validate market breadth responses and surface clear errors for missing dates, industries, or data points.
- [x] 2.3 Implement an HTTP client method for fetching stock detail rows by industry and trading date.
- [x] 2.4 Preserve selected-sector fetch failures in the final result so failed sectors are reported instead of silently dropped.

## 3. Analysis Core

- [x] 3.1 Convert raw market breadth tuples into per-sector time series keyed by trading date.
- [x] 3.2 Implement configurable weak-to-strong thresholds and analysis window settings.
- [x] 3.3 Implement weak-to-strong sector detection with evidence metrics for latest breadth, recent averages, recent low, rebound, and crossing state.
- [x] 3.4 Compute sector stock evidence including constituent count, above-MA20 count, and up/down counts.
- [x] 3.5 Normalize numeric-like A-share stock codes to six-character strings while preserving existing six-character codes.

## 4. Reporting And CLI

- [x] 4.1 Implement a readable console report that lists candidate sectors, evidence metrics, and normalized stock codes.
- [x] 4.2 Implement JSON output mode containing latest date, threshold configuration, selected sectors, evidence, stocks, and per-sector errors.
- [x] 4.3 Add CLI options for strong threshold, weak threshold, recent window, comparison window, minimum rebound, and maximum number of sectors.
- [x] 4.4 Ensure the no-candidates case prints a clear message and the latest trading date used.
- [x] 4.5 Include a data-analysis-only disclaimer in human-readable output without using buy or sell language.

## 5. Tests

- [x] 5.1 Add fixture data for market breadth responses and sector stock responses.
- [x] 5.2 Test response validation for missing or malformed market breadth fields.
- [x] 5.3 Test weak-to-strong detection for crossing, already-strong, and improving-but-still-weak sectors.
- [x] 5.4 Test stock-code normalization for numeric, decimal-like, and existing six-character codes.
- [x] 5.5 Test JSON output shape and no-candidates output behavior.
- [x] 5.6 Test that sector stock fetch failures remain visible in the final result.

## 6. Verification

- [x] 6.1 Run the unit test suite locally.
- [x] 6.2 Run the CLI against fixture data to verify deterministic output.
- [x] 6.3 Run the CLI against the live market breadth source and confirm that it produces a readable candidate-sector stock-code report.
