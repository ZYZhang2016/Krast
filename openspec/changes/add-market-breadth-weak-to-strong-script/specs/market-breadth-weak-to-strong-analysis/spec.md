## ADDED Requirements

### Requirement: Fetch Latest Market Breadth Data
The system SHALL retrieve the latest market breadth dataset from the market breadth data source and validate that it contains dates, industries, and data points.

#### Scenario: Latest breadth data is available
- **WHEN** the user runs the weak-to-strong analysis command with default options
- **THEN** the system SHALL fetch the latest breadth page and identify the latest available trading date from the returned dates

#### Scenario: Breadth response is invalid
- **WHEN** the market breadth response is missing dates, industries, or data points
- **THEN** the system MUST stop with a clear error explaining which required field is missing

### Requirement: Detect Weak-To-Strong Sectors
The system SHALL analyze recent market breadth values for each sector and select sectors that show a configurable weak-to-strong transition.

#### Scenario: Sector crosses from weak to strong
- **WHEN** a sector has recent weak readings below the weak threshold and its latest breadth is at or above the strong threshold
- **THEN** the system SHALL include the sector as a weak-to-strong candidate with evidence metrics

#### Scenario: Sector is already strong without recent weakness
- **WHEN** a sector has high recent breadth but does not have recent weak readings
- **THEN** the system SHALL exclude the sector from weak-to-strong candidates unless the configured rules explicitly allow confirmed strong sectors

#### Scenario: Sector improves but remains weak
- **WHEN** a sector improves from recent lows but its latest breadth remains below the strong threshold
- **THEN** the system SHALL exclude the sector from the default weak-to-strong candidate list

### Requirement: Fetch Candidate Sector Stocks
The system SHALL fetch stock detail rows for each selected weak-to-strong sector on the latest available trading date.

#### Scenario: Candidate sector has stock rows
- **WHEN** a weak-to-strong sector is selected
- **THEN** the system SHALL request that sector's stock rows for the latest available trading date

#### Scenario: Candidate sector stock request fails
- **WHEN** stock rows cannot be fetched for a selected sector
- **THEN** the system MUST keep the sector in the report and show an error for that sector instead of silently omitting it

### Requirement: Normalize A-Share Stock Codes
The system SHALL normalize numeric A-share stock codes to six-character strings while preserving leading zeroes.

#### Scenario: Numeric stock code is returned
- **WHEN** a stock row contains a numeric-like code such as `1.0`
- **THEN** the system SHALL render the code as `000001`

#### Scenario: Six-character stock code is returned
- **WHEN** a stock row already contains a six-character code
- **THEN** the system SHALL preserve that code unchanged

### Requirement: Report Evidence And Stock Codes
The system SHALL output a readable report containing selected sectors, signal evidence, and stock codes.

#### Scenario: Candidates are found
- **WHEN** the analysis finds one or more weak-to-strong sectors
- **THEN** the report SHALL include each sector name, latest breadth value, recent comparison metrics, constituent count, MA20 confirmation count, and normalized stock codes

#### Scenario: No candidates are found
- **WHEN** no sector satisfies the weak-to-strong rules
- **THEN** the system SHALL output a readable no-candidates message and the latest trading date used for analysis

### Requirement: Provide Machine-Readable Output
The system SHALL support a JSON output mode for automation and test verification.

#### Scenario: JSON output is requested
- **WHEN** the user selects JSON output mode
- **THEN** the system SHALL output valid JSON containing the latest date, threshold configuration, selected sectors, evidence metrics, and stocks

### Requirement: Support Configurable Thresholds
The system SHALL allow users to configure weak-to-strong thresholds and recent-window sizes without changing source code.

#### Scenario: User changes strong threshold
- **WHEN** the user provides a custom strong threshold
- **THEN** the system SHALL use that threshold when deciding whether a sector has entered the strong zone

#### Scenario: User changes analysis windows
- **WHEN** the user provides custom recent and comparison window sizes
- **THEN** the system SHALL calculate weak-to-strong evidence using those configured windows
