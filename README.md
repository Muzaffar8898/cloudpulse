# CloudPulse — Weather Data Engineering Pipeline

A Python-based data engineering project that ingests live weather data from the [Open-Meteo API](https://open-meteo.com/), validates and normalizes incoming records, and persists observations to SQLite and JSON files.

CloudPulse demonstrates core data engineering practices: API ingestion, data quality validation, structured logging, error handling, automated testing, and database persistence.

## Project Overview

CloudPulse transforms external weather data into validated, structured records that can be used for downstream analytics.

### Architecture

```text
Open-Meteo API
      |
      v
Python Ingestion
      |
      v
Data Quality Validation
      |
      v
Data Normalization
      |
      +-----------> Raw JSON Output
      |
      +-----------> Normalized JSON Output
      |
      +-----------> SQLite Database
                         |
                         v
                   SQL Analytics
                   (next milestone)
```

## Features

- **API ingestion:** Retrieves current weather observations from Open-Meteo.
- **Data quality:** Validates required fields, numeric values, humidity ranges, and non-negative wind speeds.
- **Data normalization:** Converts incoming weather data into a consistent structure.
- **Timestamping:** Records ingestion timestamps in UTC.
- **Database persistence:** Stores normalized weather observations in SQLite.
- **JSON outputs:** Saves weather data for inspection and downstream processing.
- **Logging and error handling:** Tracks pipeline execution and handles ingestion failures.
- **Automated tests:** Uses `pytest` to test validation, normalization, and pipeline behavior.
- **Code coverage:** Achieved 99% coverage of `main.py` in the current test run.
- **Version control:** Uses Git and GitHub to track source code changes.

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Ingestion and transformation |
| Open-Meteo API | External weather data source |
| SQLite | Persistent relational storage |
| JSON | Structured data exchange |
| pytest | Automated testing |
| pytest-cov | Test coverage reporting |
| Git and GitHub | Version control |
| Windows 11 / PowerShell | Development environment |

## Project Structure

```text
CloudPulse/
├── main.py                # Ingestion pipeline
├── database.py            # SQLite initialization and inserts
├── test_main.py           # Automated tests
├── README.md              # Project documentation
├── requirements.txt       # Python dependencies
├── .gitignore             # Excludes generated and local files
├── .env.example           # Environment configuration template
├── cloudpulse.db          # Generated SQLite database
├── weather_raw.json       # Generated raw output
└── weather_normalized.json # Generated normalized output
```

The database and generated JSON files are runtime artifacts and are excluded from Git using `.gitignore`. They may not be present in a fresh clone until the pipeline runs.

## Run Locally

### 1. Clone the repository

```powershell
git clone https://github.com/Muzaffar8898/cloudpulse.git
cd cloudpulse
```

### 2. Create and activate a virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install testing dependencies

If they are not already installed in your environment:

```powershell
python -m pip install requests pytest pytest-cov
```

SQLite is included with Python through the standard-library `sqlite3` module.

### 4. Run the pipeline

```powershell
python .\main.py
```

The pipeline retrieves weather data, validates and normalizes the response, initializes the SQLite database if necessary, inserts an observation, and writes JSON outputs.

### 5. Run automated tests

```powershell
python -m pytest
```

To measure test coverage:

```powershell
python -m pytest --cov=main --cov-report=term-missing
```

## Database Design

CloudPulse stores weather observations in a SQLite table named `weather_observations`.

| Column | Description |
|---|---|
| `id` | Auto-incrementing record identifier |
| `weather_time` | Timestamp associated with the weather observation |
| `ingested_at` | UTC timestamp when the pipeline ingested the record |
| `temperature_c` | Temperature in Celsius |
| `humidity_pct` | Relative humidity percentage |
| `wind_speed_kmh` | Wind speed in kilometers per hour |

Separating observation time from ingestion time is useful for identifying delays, validating freshness, and preparing for historical analytics.

## Data Quality Checks

The pipeline checks that:

- Required weather data is present.
- Temperature, humidity, and wind speed contain valid numeric values.
- Relative humidity is between 0 and 100.
- Wind speed is non-negative.
- Incoming data passes validation before being processed and persisted.

## Current Validation Results

- **Automated tests:** 23 passing
- **`main.py` test coverage:** 99%
- **SQLite persistence:** Verified with a live observation
- **Version control:** Feature committed and pushed to GitHub

These results reflect the latest local test run and should be reproduced when reviewing a fresh checkout.

## Roadmap

1. Add SQL queries for historical weather analysis and aggregation.
2. Introduce analytical exports such as CSV and Parquet.
3. Add GitHub Actions for automated testing on each push.
4. Containerize the application with Docker.
5. Explore Amazon S3 for raw-data storage and AWS-based deployment.
6. Add dashboards and monitoring for pipeline health.
7. Expand data modeling and orchestration capabilities.

## Disclaimer

CloudPulse is an educational portfolio project. Weather observations change over time, and successful ingestion depends on API availability and network connectivity.

## Author

**Muzaffar**

Computer Science Engineering background, developing practical skills in data engineering, cloud technologies, and AI.

GitHub: [Muzaffar8898/cloudpulse](https://github.com/Muzaffar8898/cloudpulse)
