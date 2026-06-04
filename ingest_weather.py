import requests
import json
from datetime import datetime
from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv
import os
import snowflake.connector

load_dotenv()

AZURE_CONNECTION_STRING = os.getenv("AZURE_CONNECTION_STRING")
CONTAINER_NAME = "raw-weather-data"

SNOWFLAKE_USER     = os.getenv("SNOWFLAKE_USER")
SNOWFLAKE_PASSWORD = os.getenv("SNOWFLAKE_PASSWORD")
SNOWFLAKE_ACCOUNT  = os.getenv("SNOWFLAKE_ACCOUNT")

url = "https://api.open-meteo.com/v1/forecast"
params = {
    "latitude": 59.33,
    "longitude": 18.07,
    "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum",
    "timezone": "Europe/Stockholm",
    "past_days": 7
}

response = requests.get(url, params=params)
weather_data = response.json()
print("Data fetched from API!")

today = datetime.now().strftime("%Y-%m-%d")
filename = f"weather_stockholm_{today}.json"

with open(filename, "w") as f:
    json.dump(weather_data, f)
print(f"Saved locally as {filename}")

blob_service_client = BlobServiceClient.from_connection_string(AZURE_CONNECTION_STRING)
blob_client = blob_service_client.get_blob_client(container=CONTAINER_NAME, blob=filename)
with open(filename, "rb") as data:
    blob_client.upload_blob(data, overwrite=True)
print(f"Uploaded to Azure Blob Storage: {filename}")

conn = snowflake.connector.connect(
    user=SNOWFLAKE_USER,
    password=SNOWFLAKE_PASSWORD,
    account=SNOWFLAKE_ACCOUNT,
    warehouse="COMPUTE_WH",
    database="WEATHER_DB",
    schema="RAW"
)

cur = conn.cursor()
cur.execute(
    "INSERT INTO WEATHER_RAW (raw_data) SELECT PARSE_JSON(%s)",
    (json.dumps(weather_data),)
)
conn.close()
print(f"Loaded into Snowflake WEATHER_DB.RAW.WEATHER_RAW!")
