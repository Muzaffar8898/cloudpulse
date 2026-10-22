import sqlite3

DATABASE_PATH = "cloudpulse.db"


def get_daily_summary(db_path=DATABASE_PATH):
    connection = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    try:
        query = """
            SELECT
                date(weather_time) AS observation_date,
                COUNT(*) AS total_observations,
                ROUND(AVG(temperature_c), 2) AS avg_temp_c,
                ROUND(AVG(humidity_pct), 2) AS avg_humidity_pct,
                ROUND(AVG(wind_speed_kmh), 2) AS avg_wind_kmh
            FROM weather_observations
            GROUP BY date(weather_time)
            ORDER BY observation_date
        """
        return connection.execute(query).fetchall()
    finally:
        connection.close()


if __name__ == "__main__":
    for row in get_daily_summary():
        print(row)
