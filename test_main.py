import main
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
def test_api_failure_is_logged(monkeypatch, caplog):
    def fail_request(*args, **kwargs):
        raise OSError("simulated network failure")

    monkeypatch.setattr(main, "urlopen", fail_request)

    with caplog.at_level("ERROR", logger="main"):
        with pytest.raises(OSError, match="simulated network failure"):
            main.main()

    assert "Failed to fetch weather data" in caplog.text
def test_fetch_weather_retries_then_succeeds(monkeypatch):
    attempts = {"count": 0}

    def flaky_request(*args, **kwargs):
        attempts["count"] += 1
        if attempts["count"] == 1:
            raise main.URLError("temporary network failure")

        class FakeResponse:
            def __enter__(self):
                return self

            def __exit__(self, *args):
                return False

        return FakeResponse()

    monkeypatch.setattr(main, "urlopen", flaky_request)
    monkeypatch.setattr(main.time, "sleep", lambda seconds: None)
    monkeypatch.setattr(main.json, "load", lambda response: {"current": {}})

    result = main.fetch_weather(max_attempts=3, delay_seconds=0)

    assert result == {"current": {}}
    assert attempts["count"] == 2


def test_fetch_weather_raises_after_all_attempts_fail(monkeypatch):
    attempts = {"count": 0}

    def failing_request(*args, **kwargs):
        attempts["count"] += 1
        raise main.URLError("simulated network failure")

    monkeypatch.setattr(main, "urlopen", failing_request)
    monkeypatch.setattr(main.time, "sleep", lambda seconds: None)

    with pytest.raises(main.URLError, match="simulated network failure"):
        main.fetch_weather(max_attempts=3, delay_seconds=0)

    assert attempts["count"] == 3
def test_fetch_weather_uses_environment_retry_count(monkeypatch):
    attempts = {"count": 0}

    def failing_request(*args, **kwargs):
        attempts["count"] += 1
        raise main.URLError("simulated network failure")

    monkeypatch.setenv("WEATHER_MAX_ATTEMPTS", "5")
    monkeypatch.setenv("WEATHER_RETRY_DELAY_SECONDS", "0")
    monkeypatch.setattr(main, "urlopen", failing_request)
    monkeypatch.setattr(main.time, "sleep", lambda seconds: None)

    with pytest.raises(main.URLError, match="simulated network failure"):
        main.fetch_weather()

    assert attempts["count"] == 5