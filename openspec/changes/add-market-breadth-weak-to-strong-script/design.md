## Context

The repository currently contains only OpenSpec scaffolding and no implemented runtime code, so this change can introduce a small, purpose-built script without migrating existing behavior.

The target workflow reads data from the public market breadth page at `https://sckd.dapanyuntu.com/`. The page renders a heatmap from JSON endpoints. Market breadth values represent the percentage of stocks in an industry whose close price is above MA20. Values below 50 are rendered green, 50 is white, and values above 50 are rendered red. Clicking a heatmap cell opens an industry stock page that retrieves stock rows for the selected industry and date.

The script should automate the manual workflow:

1. Fetch recent industry breadth series.
2. Detect sectors that moved from weak/green toward strong/red.
3. Fetch stock detail rows for those sectors on the latest trading date.
4. Report normalized stock codes and evidence.

## Goals / Non-Goals

**Goals:**

- Provide a repeatable command-line script for identifying weak-to-strong sectors and their stock codes.
- Keep the first version easy to run locally with minimal setup.
- Make the weak-to-strong decision explainable through visible metrics such as latest breadth, recent averages, recent low, rebound, and MA20 confirmation.
- Preserve A-share stock-code leading zeroes.
- Support configurable thresholds for tuning without editing the script internals.
- Include deterministic tests using fixture data so the core analysis can be validated without network access.

**Non-Goals:**

- No trading, order placement, brokerage integration, or investment advice.
- No persistent dashboard, scheduled job runner, database, or user account system in the first implementation.
- No browser automation unless direct JSON endpoints stop being sufficient.
- No guarantee that the upstream page or API remains stable.

## Decisions

### Use Python for the script

Use Python for the first implementation because the work is data retrieval, validation, time-series scoring, and report generation. A Python CLI also keeps the project easy to test and run locally.

Alternative considered: Node.js. It would also work for HTTP fetching, but the analysis and future data-science extensions fit Python more naturally.

### Organize as a small package plus CLI entry point

Implement the logic as importable modules rather than one large script:

```text
src/
  krast_market_breadth/
    cli.py
    client.py
    models.py
    analysis.py
    report.py
tests/
  fixtures/
```

Expose a command such as `krast-weak-to-strong` and optionally keep a thin script wrapper for users who prefer `python scripts/analyze_market_breadth.py`.

Alternative considered: a single standalone file. It is faster to create but makes tests, threshold tuning, and future output formats harder to maintain.

### Fetch direct JSON endpoints first

Use direct HTTP requests against the data endpoints observed from the market breadth page:

- `GET /api/api/industry_ma20_analysis_page?page=0`
- `GET /api/api/stock_daily_data_by_industry_and_date?industry=<name>&date=<date>`

The HTTP client should send browser-like headers, including `User-Agent` and `Referer`, because direct API calls without headers can return `403 Forbidden`.

Alternative considered: Playwright-driven browser scraping. It is heavier and unnecessary while JSON endpoints are available. It can be introduced later as a fallback if the API changes.

### Make signal scoring explainable and configurable

The default weak-to-strong filter should combine threshold crossing with recent improvement:

- latest breadth is at or above a strong threshold, default `50`
- the sector recently had weak readings, such as a recent low below `50`
- recent average improved versus the previous window
- rebound from recent low exceeds a minimum amount
- stock detail rows confirm a meaningful share of constituents are above MA20

Each selected sector should include evidence values, not just a score. This keeps the output reviewable and avoids a black-box signal.

Alternative considered: return only sectors that crossed from below 50 to above 50 on the latest day. That is simple but misses sectors that crossed a few sessions earlier and are now confirming strength.

### Normalize stock codes at the boundary

The stock detail endpoint can return numeric codes such as `1.0`. Normalize all numeric-like codes to six-character strings, e.g. `1.0` becomes `000001`, before rendering output or applying ordering.

Alternative considered: preserve upstream values verbatim. That would lose leading zeroes and make A-share codes inaccurate.

### Prefer text and JSON output

The default output should be a readable console report. A JSON output mode should be available for later automation and tests. CSV can be added later if a downstream spreadsheet workflow needs it.

## Risks / Trade-offs

- Upstream API changes or rate limiting -> isolate endpoint construction in `client.py`, validate response schemas, and show actionable fetch errors.
- Direct calls can return `403 Forbidden` -> send browser-like headers by default and expose a clear error if access still fails.
- Weak-to-strong thresholds may be too strict or too loose -> expose thresholds as CLI options and include evidence in output.
- Small sectors can produce noisy breadth readings -> report stock count and flag low-sample sectors in the output.
- A sector can show breadth strength while same-day price action is weak -> include constituent above-MA20 count and up/down counts so the user can inspect divergence.
- Financial interpretation risk -> label results as data analysis only and avoid buy/sell language.

## Migration Plan

This is an additive change. Implementation can be introduced without migrating existing code.

Rollback is to remove the new Python package, CLI metadata, tests, and documentation added by the implementation.

## Open Questions

- Should the default output include all candidate stocks in each selected sector, or only stocks individually above MA20?
- Should the first version include CSV export, or is console plus JSON enough?
- Should default thresholds favor early detection or higher confirmation?
