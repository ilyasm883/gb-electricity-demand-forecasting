# Live forecast with the saved XGBoost model.
# It works the same way as in notebook 06: hour 1 uses the real load of the hour before,
# the next hours use the forecasts already made (recursive forecasting).

import numpy as np
import pandas as pd


def predict_day(data, model, features, day, temperature_change=0, make_holiday=False):
    start = pd.Timestamp(day)
    end = start + pd.Timedelta(hours=24)

    # real load of the week before the day
    history = list(data[data["time"] < start]["load"].values[-168:])
    today = data[(data["time"] >= start) & (data["time"] < end)].reset_index(drop=True)

    forecasts = []
    for i in range(24):
        row = {
            "hour": today["hour"][i],
            "day_of_week": today["day_of_week"][i],
            "month": today["month"][i],
            "is_weekend": today["is_weekend"][i],
            "is_holiday": today["is_holiday"][i],
            "temperature": today["temperature"][i] + temperature_change,
            "lag1": history[-1],
            "lag24": history[-24],
            "lag168": history[-168],
            "rolling_mean_lag1_window_size24": np.mean(history[-24:]),
            "rolling_mean_lag1_window_size168": np.mean(history[-168:]),
        }
        if make_holiday:
            row["is_holiday"] = 1

        x = pd.DataFrame([row])[features]
        forecast = model.predict(x)[0]
        forecasts.append(forecast)
        history.append(forecast)

    today["forecast"] = forecasts
    return today
