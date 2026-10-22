
import sqlite3

DATABASE_PATH = "cloudpulse.db"


def initialize_database(db_path=DATABASE_PATH):
    connection = sqlite3.connect(db_path)
    try:
        with connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS weather_observations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    weather_time TEXT,
                    ingested_at TEXT NOT NULL,
                    temperature_c REAL NOT NULL,
                    humidity_pct REAL NOT NULL,
                    wind_speed_kmh REAL NOT NULL
                )
                """
            )
    finally:
        connection.close()


def insert_weather(data, ingested_at, db_path=DATABASE_PATH):
    connection = sqlite3.connect(db_path)
    try:
        with connection:
            connection.execute(
                """
                INSERT INTO weather_observations (
                    weather_time,
                    ingested_at,
                    temperature_c,
                    humidity_pct,
                    wind_speed_kmh
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    data["weather_time"],
                    ingested_at,
                    data["temperature_c"],
                    data["humidity_pct"],
                    data["wind_speed_kmh"],
                ),
            )
    finally:
        connection.close()
