# Stockholm Weather Data Pipeline

This is my data engineering project for Hyper Island. I built an automated pipeline that fetches weather data for Stockholm every morning and moves it through a full data stack — from a raw API call all the way to a live dashboard.

The whole thing runs on its own every day without me doing anything manually.

## How it works

Every morning at 7am Stockholm time, a Python script runs automatically via GitHub Actions. It calls the Open-Meteo weather API (free, no API key needed) and gets the last 7 days of weather data for Stockholm as a JSON file. That file gets saved to Azure Blob Storage and loaded into Snowflake.

Then at 8am, dbt Cloud wakes up and transforms that raw data. First it cleans it up and unpacks the JSON into proper columns (Silver layer), then it builds the final table with some extra calculated fields like daily temperature range and precipitation category (Gold layer).

The Streamlit dashboard reads directly from that final table in Snowflake, so it updates automatically every morning after the dbt run.

## The stack

- **Open-Meteo API** — free weather API, no account needed
- **Python + GitHub Actions** — ingestion script that runs on a cron schedule
- **Azure Blob Storage** — stores the raw JSON files (Bronze layer)
- **Snowflake** — the data warehouse where everything lives
- **dbt Cloud** — handles all the transformations and runs automated tests
- **Streamlit** — the dashboard, lives inside Snowflake

## Medallion Architecture

| Layer | What it is | What happens there |
|-------|------------|-------------------|
| Bronze | Azure Blob Storage | Raw JSON saved exactly as received |
| Silver | dbt staging model (stg_weather) | JSON unpacked, nulls handled, duplicates removed |
| Gold | dbt mart model (mart_weather_daily) | Clean data + calculated fields, what the dashboard reads |

## Data quality

dbt runs 9 tests every time it builds. It checks that the date column is never null and never duplicated, and that all the temperature and precipitation columns have values. If any test fails the run stops and the bad data never makes it to the dashboard.

## Files

```
ingest_weather.py           the Python ingestion script
.github/workflows/          GitHub Actions workflow (runs at 5am UTC / 7am Stockholm)
models/                     dbt SQL models
dbt_project.yml             dbt config
```

## Data source

Open-Meteo: https://open-meteo.com
Stockholm coordinates: lat 59.33, lon 18.07
