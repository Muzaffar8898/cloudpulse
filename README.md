\# CloudPulse — Data Engineering Pipeline



A Python-based data ingestion project that retrieves live weather data from the Open-Meteo API, validates data quality, and stores the results as structured JSON for downstream processing.



\## Project Overview



CloudPulse demonstrates the foundations of a reliable data engineering pipeline: API ingestion, input validation, UTC timestamping, structured storage, and version control.



\## Architecture



Open-Meteo API → Python Ingestion → Data Quality Checks → JSON Output → GitHub



\## Features



\- Retrieves current weather data from a public API.

\- Validates required fields and numeric data types.

\- Checks humidity ranges and prevents negative wind speeds.

\- Adds a UTC ingestion timestamp.

\- Stores the ingested data as formatted JSON.

\- Uses Git and GitHub for version control.

\- Excludes generated data and environment files from version control.



\## Technology Stack



\- \*\*Language:\*\* Python

\- \*\*Data source:\*\* Open-Meteo API

\- \*\*Data format:\*\* JSON

\- \*\*Version control:\*\* Git and GitHub

\- \*\*Development environment:\*\* Windows 11



\## Run Locally



\### 1. Clone the repository



```bash

git clone https://github.com/Muzaffar8898/cloudpulse.git

cd cloudpulse

```



\### 2. Create and activate a virtual environment



On Windows PowerShell:



```powershell

python -m venv .venv

.\\.venv\\Scripts\\Activate.ps1

```



\### 3. Run the pipeline



```powershell

python .\\main.py

```



The script retrieves current weather data, runs validation checks, and generates `weather\_raw.json` in the project directory.



\## Data Quality Checks



The pipeline verifies that:

\- Current weather data exists.

\- Temperature, humidity, and wind speed are numeric.

\- Relative humidity is between 0 and 100.

\- Wind speed is non-negative.



\## Planned Improvements



\- Add automated unit tests with `pytest`.

\- Implement structured logging and retry handling.

\- Store raw data in Amazon S3.

\- Transform JSON into Parquet for analytical workloads.

\- Add SQL-based transformations and data modeling with dbt.

\- Introduce Docker-based orchestration and automated CI checks.

\- Add monitoring, documentation, and cloud security controls.



\## Disclaimer



This is an educational portfolio project. Weather observations vary over time, and the API must be reachable for ingestion to succeed.



\## Author



\*\*Muzaffar\*\* — Computer Science Engineering background, building practical skills in data engineering, cloud technologies, and AI.



