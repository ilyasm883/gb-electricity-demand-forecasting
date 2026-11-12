# Downloads the newest GB demand and temperature, so the app can also forecast the latest days.
# Demand: Elexon (the GB electricity market data service), "actual total load", every half hour.
# Temperature: Open-Meteo, average of eight big UK cities.
# Both are free and need no account. The result has the same columns as the saved 2015-2019 data.
# It also adds today and the next 6 days. These days have a weather forecast but no real demand yet.

import holidays
import pandas as pd
import requests
import streamlit as st

demand_url = "https://data.elexon.co.uk/bmrs/api/v1/demand/actual/total"
weather_url = "https://archive-api.open-meteo.com/v1/archive"
weather_forecast_url = "https://api.open-meteo.com/v1/forecast"

# how many days back we download (the model needs the week before the day it forecasts)
days_back = 42
# how many future days we add (today is the first one)
days_ahead = 7

# eight big cities, spread over Great Britain
city_latitudes = "51.51,52.48,53.48,53.80,55.86,51.45,54.98,51.48"
city_longitudes = "-0.13,-1.90,-2.24,-1.55,-4.25,-2.59,-1.61,-3.18"


def download_demand(first_day, last_day):
    # the service gives at most 7 days at a time, so we ask week by week
    parts = []
    start = first_day
    while start <= last_day:
        end = min(start + pd.Timedelta(days=7), last_day + pd.Timedelta(days=1))
        answer = requests.get(demand_url, params={
            "from": start.strftime("%Y-%m-%dT00:00Z"),
            "to": end.strftime("%Y-%m-%dT00:00Z"),
            "format": "json",
        }, timeout=60)
        parts.append(pd.DataFrame(answer.json()["data"]))
        start = end

    demand = pd.concat(parts)
    demand["time"] = pd.to_datetime(demand["startTime"]).dt.tz_localize(None)
    demand = demand.drop_duplicates("time").sort_values("time")

    # values this low are mistakes in the source (the real demand is never below 12,000 MW)
    demand = demand[demand["quantity"] >= 12000]

    # two half hours make one hour
    hourly = demand.set_index("time")["quantity"].resample("1h").mean()
    return hourly


def download_temperature(url, first_day, last_day):
    answer = requests.get(url, params={
        "latitude": city_latitudes,
        "longitude": city_longitudes,
        "start_date": first_day.strftime("%Y-%m-%d"),
        "end_date": last_day.strftime("%Y-%m-%d"),
        "hourly": "temperature_2m",
        "timezone": "UTC",
    }, timeout=60)
    cities = answer.json()

    temperature = pd.DataFrame()
    for i in range(len(cities)):
        temperature["city" + str(i)] = cities[i]["hourly"]["temperature_2m"]
    temperature.index = pd.to_datetime(cities[0]["hourly"]["time"])
    return temperature.mean(axis=1)


# keep the download for 3 hours, then get it again
@st.cache_data(ttl=3 * 60 * 60, show_spinner="Downloading the latest demand and temperature...")
def load_live_data():
    try:
        today = pd.Timestamp.now(tz="UTC").tz_localize(None).normalize()
        last_day = today - pd.Timedelta(days=1)
        first_day = last_day - pd.Timedelta(days=days_back)

        load = download_demand(first_day, last_day)
        temperature = download_temperature(weather_url, first_day, last_day)

        # one row for every hour, also for hours that are missing in the source
        hours = pd.date_range(first_day, last_day + pd.Timedelta(hours=23), freq="1h")
        data = pd.DataFrame({"time": hours})
        data["load"] = load.reindex(hours).values
        data["temperature"] = temperature.reindex(hours).values

        # one-hour spikes: far away from both neighbours in the same direction (same rule as notebook 02)
        change_from_previous = data["load"] - data["load"].shift(1)
        change_to_next = data["load"] - data["load"].shift(-1)
        spike_up = (change_from_previous > 5000) & (change_to_next > 5000)
        spike_down = (change_from_previous < -5000) & (change_to_next < -5000)
        data.loc[spike_up | spike_down, "load"] = None

        # fill the missing hours with a straight line between the hours around them
        data["was_filled"] = data["load"].isnull().astype(int)
        data["load"] = data["load"].interpolate(limit_direction="both")
        data["temperature"] = data["temperature"].interpolate(limit_direction="both")

        # today and the next days: temperature from the weather forecast, real demand is not known yet
        last_future_day = today + pd.Timedelta(days=days_ahead - 1)
        future_temperature = download_temperature(weather_forecast_url, today, last_future_day)
        future_hours = pd.date_range(today, last_future_day + pd.Timedelta(hours=23), freq="1h")
        future = pd.DataFrame({"time": future_hours})
        future["load"] = float("nan")
        future["temperature"] = future_temperature.reindex(future_hours).interpolate(limit_direction="both").values
        future["was_filled"] = 0
        data = pd.concat([data, future], ignore_index=True)

        # the same calendar features as in notebook 04
        bank_holidays = holidays.UK(subdiv="ENG", years=[first_day.year, last_future_day.year])
        data["hour"] = data["time"].dt.hour
        data["day_of_week"] = data["time"].dt.dayofweek
        data["month"] = data["time"].dt.month
        data["is_weekend"] = (data["day_of_week"] >= 5).astype(int)
        data["is_holiday"] = data["time"].dt.date.isin(list(bank_holidays.keys())).astype(int)
        return data
    except Exception:
        # no internet, or the data service does not answer
        return None
