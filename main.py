import json
from datetime import datetime, timezone
from urllib.request import urlopen

API_URL = (
    "https://api.open-meteo.com/v1/forecast"
    "?latitude=38.6270&longitude=-90.1994"
    "&current=temperature_2m,relative_humidity_2m,wind_speed_10m"
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
def main():
    with urlopen(API_URL, timeout=20) as response:
        data = json.load(response)

    current = data.get("current")
    validate_weather(current)
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
    print("Saved validated data to weather_raw.json")

if __name__ == "__main__":
    main()
