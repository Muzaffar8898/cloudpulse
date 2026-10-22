import json
import logging
import time
import os
from urllib.error import URLError, HTTPError
from datetime import datetime, timezone
from urllib.request import urlopen

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s - %(message)s",
)

logger = logging.getLogger(__name__)

API_URL = os.getenv(
    "WEATHER_API_URL",
    "https://api.open-meteo.com/v1/forecast?latitude=38.6270&longitude=-90.1994&current=temperature_2m,relative_humidity_2m,wind_speed_10m",
)

def validate_weather(current):
    if not isinstance(current, dict):
        raise ValueError("Data quality check failed: current weather is missing")

    required_fields = [
        "temperature_2m",
        "relative_humidity_2m",
        "wind_speed_10m",
    ]

    for field in required_fields:
        value = current.get(field)
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError(f"Data quality check failed: {field} must be numeric")

    if not 0 <= current["relative_humidity_2m"] <= 100:
        raise ValueError("Data quality check failed: humidity is out of range")

    if current["wind_speed_10m"] < 0:
        raise ValueError("Data quality check failed: wind speed cannot be negative")
def fetch_weather(
    max_attempts=None,
    delay_seconds=None,
):
    if max_attempts is None:
        max_attempts = int(os.getenv("WEATHER_MAX_ATTEMPTS", "3"))

    if delay_seconds is None:
        delay_seconds = float(os.getenv("WEATHER_RETRY_DELAY_SECONDS", "2"))
    for attempt in range(1, max_attempts + 1):
        try:
            with urlopen(API_URL, timeout=20) as response:
                return json.load(response)

        except (URLError, TimeoutError) as exc:
            logger.warning(
                "Weather API request failed (attempt %s/%s): %s",
                attempt,
                max_attempts,
                exc,
            )

            if attempt == max_attempts:
                logger.error("Weather API request failed after all retries")
                raise

            time.sleep(delay_seconds)
def main():
    logger.info("Starting CloudPulse weather ingestion")
    try:
        data = fetch_weather()
    except Exception:
        logger.exception("Failed to fetch weather data")
        raise

    current = data.get("current")
    validate_weather(current)
    logger.info("Weather data quality checks passed")
    
    record = {
        "source": "open-meteo",
        "ingested_at": datetime.now(timezone.utc).isoformat(),
        "weather": data,
    }

    with open("weather_raw.json", "w", encoding="utf-8") as file:
        json.dump(record, file, indent=2)

    print("Data quality checks passed!")
    print(f"Temperature: {current['temperature_2m']} °C")
    print(f"Humidity: {current['relative_humidity_2m']}%")
    print(f"Wind speed: {current['wind_speed_10m']} km/h")
    logger.info("Saved validated data to weather_raw.json")
    print("Saved validated data to weather_raw.json")

if __name__ == "__main__":
    main()
