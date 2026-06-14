## Why

The current market breadth analysis is an ad hoc manual workflow: inspect the heatmap, infer sectors that are shifting from green to red, open each sector page, and copy stock codes. This change turns that repeatable workflow into a script so weak-to-strong sector and stock-code discovery can be run consistently from the command line.

## What Changes

- Add a command-line script that fetches A-share market breadth data from the market breadth page data endpoints.
- Analyze recent sector breadth series to identify sectors transitioning from weak to strong.
- Fetch stock detail data for selected weak-to-strong sectors on the latest available trading date.
- Normalize A-share stock codes to six-character strings while preserving leading zeroes.
- Output a human-readable summary of candidate sectors, evidence, and stock codes.
- Provide configurable thresholds for recent-window analysis without requiring code edits.

## Capabilities

### New Capabilities

- `market-breadth-weak-to-strong-analysis`: Detect weak-to-strong sectors from market breadth data and report the corresponding sector stock codes.

### Modified Capabilities

None.

## Impact

- Adds a script-oriented market breadth analysis workflow to the repository.
- Introduces HTTP data retrieval, response validation, sector signal scoring, stock-code normalization, and report rendering.
- May add Python project metadata and runtime dependencies for HTTP requests, CLI parsing, and tests.
- Does not change any existing application behavior because the repository currently has no implemented runtime code.
