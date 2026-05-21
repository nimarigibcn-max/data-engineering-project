import requests
import json
from datetime import datetime
from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv
import os

# Load the secret connection string from the .env file
load_dotenv()
AZURE_CONNECTION_STRING = os.getenv("AZURE_CONNECTION_STRING")
CONTAINER_NAME = "raw-weather-data"

# --- STEP 1: Fetch weather data from Open-Meteo API ---
url = "https://api.open-meteo.com/v1/forecast"
params = {
    "latitude": 59.33,       # Stockholm
    "longitude": 18.07,
    "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum",
    "timezone": "Europe/Stockholm",
    "past_days": 7           # Get the last 7 days of data
}

response = requests.get(url, params=params)
weather_data = response.json()
print("Data fetched from API!")

# --- STEP 2: Save data as a JSON file with today's date in the name ---
today = datetime.now().strftime("%Y-%m-%d")
filename = f"weather_stockholm_{today}.json"

with open(filename, "w") as f:
    json.dump(weather_data, f)
print(f"Saved locally as {filename}")

# --- STEP 3: Upload the file to Azure Blob Storage ---
blob_service_client = BlobServiceClient.from_connection_string(AZURE_CONNECTION_STRING)
blob_client = blob_service_client.get_blob_client(container=CONTAINER_NAME, blob=filename)

with open(filename, "rb") as data:
    blob_client.upload_blob(data, overwrite=True)
print(f"Uploaded to Azure Blob Storage: {filename}")
