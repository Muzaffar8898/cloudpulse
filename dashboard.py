import sqlite3
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from analytics import get_daily_summary, DATABASE_PATH


st.set_page_config(
    page_title="CloudPulse Analytics",
    page_icon="🌦️",
    layout="wide",
)

st.title("🌦️ CloudPulse Analytics")
st.caption("Weather ingestion and daily analytics dashboard")

demo_path = Path("cloudpulse_demo.db")
db_path = demo_path if demo_path.exists() else Path(DATABASE_PATH)

if not db_path.exists():
    st.warning(
        "No weather database found yet. Run `python main.py` "
        "from your project folder to collect an observation."
    )
    st.stop()

try:
    daily_rows = get_daily_summary(str(db_path))
    with sqlite3.connect(
        f"file:{db_path.resolve().as_posix()}?mode=ro",
        uri=True,
    ) as connection:
        raw_rows = connection.execute(
            """
            SELECT weather_time, ingested_at, temperature_c,
                   humidity_pct, wind_speed_kmh
            FROM weather_observations
            ORDER BY weather_time
            """
        ).fetchall()
except (sqlite3.Error, OSError) as exc:
    st.error(f"Unable to read the weather database: {exc}")
    st.stop()

daily_columns = [
    "Date",
    "Observations",
    "Avg Temperature (°C)",
    "Avg Humidity (%)",
    "Avg Wind (km/h)",
]
daily = pd.DataFrame(daily_rows, columns=daily_columns)

raw_columns = [
    "Observation Time",
    "Ingested At",
    "Temperature (°C)",
    "Humidity (%)",
    "Wind Speed (km/h)",
]
observations = pd.DataFrame(raw_rows, columns=raw_columns)

if observations.empty:
    st.info("The database has no observations yet. Run the ingestion pipeline first.")
    st.stop()

observations["Observation Time"] = pd.to_datetime(
    observations["Observation Time"], errors="coerce", utc=True
)
observations = observations.dropna(subset=["Observation Time"])

if observations.empty:
    st.warning("No valid observation timestamps are available to chart.")
    st.stop()

latest = observations.iloc[-1]

col1, col2, col3, col4 = st.columns(4)
col1.metric("Latest temperature", f"{latest['Temperature (°C)']:.1f} °C")
col2.metric("Latest humidity", f"{latest['Humidity (%)']:.0f}%")
col3.metric("Latest wind", f"{latest['Wind Speed (km/h)']:.1f} km/h")
col4.metric("Total observations", f"{len(observations):,}")

st.subheader("Weather trends")

temperature_chart = px.line(
    observations,
    x="Observation Time",
    y="Temperature (°C)",
    markers=True,
    title="Temperature over time",
)
st.plotly_chart(temperature_chart, use_container_width=True)

left, right = st.columns(2)

with left:
    humidity_chart = px.line(
        observations,
        x="Observation Time",
        y="Humidity (%)",
        markers=True,
        title="Humidity over time",
    )
    st.plotly_chart(humidity_chart, use_container_width=True)

with right:
    wind_chart = px.line(
        observations,
        x="Observation Time",
        y="Wind Speed (km/h)",
        markers=True,
        title="Wind speed over time",
    )
    st.plotly_chart(wind_chart, use_container_width=True)

st.subheader("Daily SQL summary")
if not daily.empty:
    st.dataframe(daily, use_container_width=True, hide_index=True)
    daily_chart = px.bar(
        daily,
        x="Date",
        y="Observations",
        title="Observations collected per day",
    )
    st.plotly_chart(daily_chart, use_container_width=True)
else:
    st.info("Daily summaries will appear when observations are available.")

with st.expander("View raw observations"):
    st.dataframe(observations, use_container_width=True, hide_index=True)

st.caption("Data source: local SQLite database. Charts reflect stored observations.")


