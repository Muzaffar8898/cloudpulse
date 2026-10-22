import csv

from export_csv import export_daily_summary


def test_export_daily_summary_writes_header_and_rows(tmp_path, monkeypatch):
    expected_rows = [
        ("2026-10-22", 2, 23.7, 36.5, 2.4),
    ]

    monkeypatch.setattr(
        "export_csv.get_daily_summary",
        lambda: expected_rows,
    )

    output_path = tmp_path / "summary.csv"
    returned_path = export_daily_summary(str(output_path))

    assert returned_path == str(output_path)

    with output_path.open("r", newline="", encoding="utf-8") as csvfile:
        rows = list(csv.reader(csvfile))

    assert rows == [
        [
            "observation_date",
            "total_observations",
            "avg_temp_c",
            "avg_humidity_pct",
            "avg_wind_kmh",
        ],
        ["2026-10-22", "2", "23.7", "36.5", "2.4"],
    ]
