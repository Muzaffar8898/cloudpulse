import sqlite3
import subprocess
import sys

from analytics import get_daily_summary


def test_daily_summary_aggregates_observations(tmp_path):
    db_path = tmp_path / "test_weather.db"

    connection = sqlite3.connect(db_path)
    try:
        connection.execute("""
            CREATE TABLE weather_observations (
                id INTEGER PRIMARY KEY,
                weather_time TEXT,
                ingested_at TEXT NOT NULL,
                temperature_c REAL NOT NULL,
                humidity_pct REAL NOT NULL,
                wind_speed_kmh REAL NOT NULL
            )
        """)

        connection.executemany(
            """
            INSERT INTO weather_observations
            (weather_time, ingested_at, temperature_c,
             humidity_pct, wind_speed_kmh)
            VALUES (?, ?, ?, ?, ?)
            """,
            [
                ("2026-10-22T10:00", "2026-10-22T10:01Z", 20, 40, 2),
                ("2026-10-22T11:00", "2026-10-22T11:01Z", 24, 60, 4),
                ("2026-10-23T10:00", "2026-10-23T10:01Z", 18, 50, 3),
            ],
        )
        connection.commit()
    finally:
        connection.close()

    result = get_daily_summary(str(db_path))

    assert result == [
        ("2026-10-22", 2, 22.0, 50.0, 3.0),
        ("2026-10-23", 1, 18.0, 50.0, 3.0),
    ]
def test_script_runs_and_prints_daily_summary(tmp_path):
    db_path = tmp_path / "cloudpulse.db"

    connection = sqlite3.connect(db_path)
    try:
        connection.execute("""
            CREATE TABLE weather_observations (
                id INTEGER PRIMARY KEY,
                weather_time TEXT,
                ingested_at TEXT NOT NULL,
                temperature_c REAL NOT NULL,
                humidity_pct REAL NOT NULL,
                wind_speed_kmh REAL NOT NULL
            )
        """)
        connection.execute(
            """
            INSERT INTO weather_observations
            (weather_time, ingested_at, temperature_c,
             humidity_pct, wind_speed_kmh)
            VALUES (?, ?, ?, ?, ?)
            """,
            ("2026-10-22T10:00", "2026-10-22T10:01Z", 20, 40, 2),
        )
        connection.commit()
    finally:
        connection.close()

    result = get_daily_summary(str(db_path))
    assert result == [("2026-10-22", 1, 20.0, 40.0, 2.0)]
