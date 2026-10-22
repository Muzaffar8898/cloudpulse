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
def test_invalid_retry_count_is_rejected(monkeypatch):
    monkeypatch.setenv("WEATHER_MAX_ATTEMPTS", "abc")
    monkeypatch.setenv("WEATHER_RETRY_DELAY_SECONDS", "2")

    with pytest.raises(ValueError, match="Retry configuration"):
        main.get_retry_config()
def test_zero_retry_count_is_rejected(monkeypatch):
    monkeypatch.setenv("WEATHER_MAX_ATTEMPTS", "0")
    monkeypatch.setenv("WEATHER_RETRY_DELAY_SECONDS", "2")

    with pytest.raises(ValueError, match="at least 1"):
        main.get_retry_config()
def test_negative_retry_delay_is_rejected(monkeypatch):
    monkeypatch.setenv("WEATHER_MAX_ATTEMPTS", "3")
    monkeypatch.setenv("WEATHER_RETRY_DELAY_SECONDS", "-1")

    with pytest.raises(ValueError, match="between 0 and 60"):
        main.get_retry_config()
def test_retry_delay_over_60_seconds_is_rejected(monkeypatch):
    monkeypatch.setenv("WEATHER_MAX_ATTEMPTS", "3")
    monkeypatch.setenv("WEATHER_RETRY_DELAY_SECONDS", "61")

    with pytest.raises(ValueError, match="between 0 and 60"):
        main.get_retry_config()
def test_http_error_is_not_retried(monkeypatch, caplog):
    attempts = {"count": 0}

    def failing_request(*args, **kwargs):
        attempts["count"] += 1
        raise main.HTTPError(
            "https://example.com",
            404,
            "Not Found",
            None,
            None,
        )

    monkeypatch.setattr(main, "urlopen", failing_request)

    with pytest.raises(main.HTTPError):
        main.fetch_weather(max_attempts=3, delay_seconds=0)

    assert attempts["count"] == 1
    assert "HTTP status 404" in caplog.text
def test_malformed_json_is_not_retried(monkeypatch):
    attempts = {"count": 0}

    class FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

    def malformed_response(*args, **kwargs):
        attempts["count"] += 1
        return FakeResponse()

    def invalid_json(response):
        raise main.json.JSONDecodeError(
            "Invalid JSON",
            "not-json",
            0,
        )

    monkeypatch.setattr(main, "urlopen", malformed_response)
    monkeypatch.setattr(main.json, "load", invalid_json)

    with pytest.raises(main.json.JSONDecodeError):
        main.fetch_weather(max_attempts=3, delay_seconds=0)

    assert attempts["count"] == 1

def test_main_saves_validated_weather(monkeypatch, tmp_path):
    weather_data = {
        "current": valid_weather(),
    }

    monkeypatch.setattr(main, "fetch_weather", lambda: weather_data)
    monkeypatch.chdir(tmp_path)

    main.main()

    output_file = tmp_path / "weather_raw.json"
    assert output_file.exists()

    import json

    saved_record = json.loads(output_file.read_text(encoding="utf-8"))

    assert saved_record["source"] == "open-meteo"
    assert saved_record["weather"] == weather_data
    assert "ingested_at" in saved_record

def test_normalize_weather_returns_standardized_fields():
    data = {
        "current": {
            **valid_weather(),
            "time": "2026-10-22T12:00",
        }
    }

    result = main.normalize_weather(data)

    assert result == {
        "temperature_c": 21.3,
        "humidity_pct": 52,
        "wind_speed_kmh": 6.6,
        "weather_time": "2026-10-22T12:00",
    }

def test_normalize_weather_rejects_invalid_data():
    data = {
        "current": {
            **valid_weather(),
            "relative_humidity_2m": 150,
        }
    }

    with pytest.raises(ValueError, match="humidity is out of range"):
        main.normalize_weather(data)

def test_insert_weather_stores_normalized_record(tmp_path):
    import sqlite3
    from database import initialize_database, insert_weather

    db_path = str(tmp_path / "test_weather.db")
    initialize_database(db_path)

    weather = {
        "weather_time": "2026-10-22T17:15",
        "temperature_c": 22.3,
        "humidity_pct": 44,
        "wind_speed_kmh": 2.6,
    }

    insert_weather(weather, "2026-10-22T17:20:00+00:00", db_path)

    connection = sqlite3.connect(db_path)
    try:
        row = connection.execute(
            """
            SELECT weather_time, temperature_c, humidity_pct, wind_speed_kmh
            FROM weather_observations
            """
        ).fetchone()
    finally:
        connection.close()

    assert row == ("2026-10-22T17:15", 22.3, 44.0, 2.6)

