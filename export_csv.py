import csv

from analytics import get_daily_summary


def export_daily_summary(output_path="daily_weather_summary.csv"):
    rows = get_daily_summary()

    with open(output_path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([
            "observation_date",
            "total_observations",
            "avg_temp_c",
            "avg_humidity_pct",
            "avg_wind_kmh",
        ])
        writer.writerows(rows)

    return output_path


if __name__ == "__main__":
    print(f"CSV report created: {export_daily_summary()}")
