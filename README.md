# Stockholm Weather Data Pipeline

An automated end-to-end data pipeline that fetches daily weather data for Stockholm, stores and transforms it using a Medallion Architecture, and visualizes it in a live Streamlit dashboard.

## Pipeline Overview

```
Open-Meteo API → Python (GitHub Actions) → Azure Blob Storage → Snowflake → dbt Cloud → Streamlit
```

The pipeline runs automatically every morning — no manual steps required.

## Architecture: Medallion Layers

| Layer | Tool | Description |
|-------|------|-------------|
| Bronze | Azure Blob Storage | Raw JSON files stored as-is, one file per day |
| Silver | dbt (stg_weather) | JSON unpacked into clean columns, NULLs handled, duplicates removed |
| Gold | dbt (mart_weather_daily) | Business-ready table with calculated metrics |

## Tools Used

- **Python** — fetches weather data from Open-Meteo API and loads it into Azure Blob and Snowflake
- **GitHub Actions** — runs the Python script automatically every day at 7am Stockholm time (5am UTC)
- **Azure Blob Storage** — stores raw JSON files as the Bronze layer
- **Snowflake** — cloud data warehouse where all layers are stored
- **dbt Cloud** — transforms raw data into Silver and Gold layers, runs automated tests
- **Streamlit** — live dashboard connected directly to Snowflake, auto-updates daily

## Automation Schedule

1. **7:00 Stockholm (5am UTC)** — GitHub Actions triggers `ingest_weather.py`
2. **8:00 Stockholm (6am UTC)** — dbt Cloud runs `dbt build` (Silver + Gold updated)
3. **Always live** — Streamlit reads from the Gold table in Snowflake

## Data Quality

dbt runs 9 automated tests on every build:
- `not_null` and `unique` checks on the date column in both models
- `not_null` checks on all key columns (temperature max, min, precipitation)

All tests must pass before data reaches the Gold layer.

## Project Structure

```
.github/workflows/    # GitHub Actions workflow (ingest.yml)
models/               # dbt SQL models (stg_weather, mart_weather_daily)
ingest_weather.py     # Python ingestion script
dbt_project.yml       # dbt project configuration
```

## Data Source

[Open-Meteo](https://open-meteo.com/) — free weather API, no API key required.
Location: Stockholm (lat 59.33, lon 18.07)
Fields: temperature max/min, precipitation sum (past_days=7 per run)
