import pytest
from main import validate_weather


def valid_weather():
    return {
        "temperature_2m": 21.3,
        "relative_humidity_2m": 52,
        "wind_speed_10m": 6.6,
    }


def test_valid_weather_passes():
    validate_weather(valid_weather())


@pytest.mark.parametrize(
    "field",
    ["temperature_2m", "relative_humidity_2m", "wind_speed_10m"],
)
def test_missing_field_is_rejected(field):
    current = valid_weather()
    del current[field]

    with pytest.raises(ValueError, match="must be numeric"):
        validate_weather(current)


@pytest.mark.parametrize("humidity", [-1, 101])
def test_invalid_humidity_is_rejected(humidity):
    current = valid_weather()
    current["relative_humidity_2m"] = humidity

    with pytest.raises(ValueError, match="humidity is out of range"):
        validate_weather(current)


def test_negative_wind_speed_is_rejected():
    current = valid_weather()
    current["wind_speed_10m"] = -1

    with pytest.raises(ValueError, match="wind speed cannot be negative"):
        validate_weather(current)


def test_boolean_temperature_is_rejected():
    current = valid_weather()
    current["temperature_2m"] = True

    with pytest.raises(ValueError, match="must be numeric"):
        validate_weather(current)


def test_missing_current_weather_is_rejected():
    with pytest.raises(ValueError, match="current weather is missing"):
        validate_weather(None)