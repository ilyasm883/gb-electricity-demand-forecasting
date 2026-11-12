# Page 1: live 24-hour forecast with XGBoost, with temperature and bank holiday "what if" controls

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from predictor import predict_day, predict_future_day
from live_data import load_live_data


def show(data, model, features):
    st.title("Prediction")
    st.subheader("Forecast one day with XGBoost")

    st.success(
        "**Model used on this page: XGBoost.**\n\n"
        "XGBoost is the most accurate of the five models in this project. It has the lowest error on the test year 2019. "
        "Only XGBoost makes the forecast on this page. The other four models (seasonal naive, SARIMA, LSTM and PatchTST) "
        "are not used here. You can see their forecasts on the **Compare models** page."
    )

    st.info(
        "**How the forecast works**\n\n"
        "1. You choose a day: a day of the test year 2019, one of the latest days, or a future day (today and the next 6 days).\n"
        "2. XGBoost looks at the real demand of the week before that day.\n"
        "3. It also uses the hour, day of the week, month, bank holiday and temperature of each hour.\n"
        "4. It forecasts the demand for each of the 24 hours of that day.\n"
        "5. The black line shows the real demand, so you can see how close the forecast is. "
        "A future day has no real demand yet, so only the forecast is shown.\n\n"
        "**Try it:** change the temperature or mark the day as a bank holiday. XGBoost makes a new forecast "
        "and the numbers below show how much it changed."
    )

    # which days: the saved test year, or the newest days from the internet
    period = st.radio("Which days do you want to forecast?",
                      ["Test year 2019 (saved data)", "Latest and future days (live data)"], horizontal=True)
    live = period.startswith("Latest")

    first_day = pd.Timestamp("2019-01-01")
    last_day = pd.Timestamp("2019-12-31")
    start_day = pd.Timestamp("2019-02-06")

    if live:
        live_data = load_live_data()
        if live_data is None:
            st.error("The latest data could not be downloaded. Check the internet connection and try again, "
                     "or choose the test year 2019.")
            return
        data = live_data
        # the model needs the 7 days before the day it forecasts
        first_day = data["time"].min() + pd.Timedelta(days=7)
        last_day = data["time"].max().normalize()
        # yesterday is the last day with real demand
        last_real_day = data[data["load"].notnull()]["time"].max().normalize()
        start_day = last_real_day

        st.warning(
            "**Live data: please read this.**\n\n"
            "- These days are **not** part of the tested results. All results in this project are for the test year 2019.\n"
            "- XGBoost was trained on data from 2015 to 2017 and it is not trained again here. Electricity use has changed "
            "since then, so the error on the latest days is usually bigger than in 2019 (about twice as big on average).\n"
            "- The demand comes from Elexon and the temperature from Open-Meteo (average of eight big UK cities). "
            "These are not the same sources as the 2015-2019 data.\n"
            "- Some hours are missing in the live demand. They are filled with a straight line between the hours around them.\n"
            "- **Future days** (today and the next 6 days) have no real demand yet. For these days the page shows "
            "**only the forecast**: no actual line and no error."
        )

        with st.expander("How the real demand after 2019 is collected", expanded=True):
            st.markdown(
                "The saved project data stops on 31 December 2019. For the latest days, the app downloads the data "
                "from the internet when you open this option.\n\n"
                "**Real demand (the black \"Actual\" line)**\n\n"
                "1. The grid operator measures how much electricity Great Britain uses in every half hour.\n"
                "2. **Elexon**, the official data service of the GB electricity market, publishes each measured value "
                "about two hours later. The dataset is called **Actual Total Load**.\n"
                "3. The app asks Elexon for the last 42 days, ending yesterday. This is free and needs no account. "
                "The address is `https://data.elexon.co.uk/bmrs/api/v1/demand/actual/total`.\n"
                "4. The two half-hour values of each hour are averaged into one hourly value, because the model works with hours.\n"
                "5. Values that are clearly wrong (below 12,000 MW, or a one-hour spike of more than 5,000 MW) are removed.\n"
                "6. Missing hours are filled with a straight line between the hours around them.\n\n"
                "**Temperature**\n\n"
                "The hourly temperature comes from **Open-Meteo**, a free weather data service. The app takes the average of "
                "eight big cities: London, Birmingham, Manchester, Leeds, Glasgow, Bristol, Newcastle and Cardiff.\n\n"
                "**Bank holidays**\n\n"
                "The bank holidays of England come from the Python package `holidays`, the same as in the notebooks.\n\n"
                "**What is not in the app**\n\n"
                "**Future days (today and the next 6 days)**\n\n"
                "- There is no real demand for these days yet, so the page shows only the forecast.\n"
                "- The temperature is the **weather forecast** from Open-Meteo for the same eight cities.\n"
                "- For today, XGBoost starts from the real demand up to yesterday.\n"
                "- For a later day, XGBoost first forecasts the days in between and then uses these forecasts "
                "in place of the real demand. So the further ahead the day, the less exact the forecast.\n\n"
                "**What is not in the app**\n\n"
                "- Only the last 42 days are downloaded. The days between 2020 and then are not in the app.\n"
                "- Today counts as a future day, because the day is not finished and its real demand is not complete yet.\n"
                "- Nothing is saved in the project. The download is kept for 3 hours and then done again."
            )

    # user choices
    col1, col2, col3 = st.columns(3)
    day = col1.date_input("Day to forecast", value=start_day, min_value=first_day, max_value=last_day)
    temperature_change = col2.slider("Temperature change (°C)", -10, 10, 0,
                                     help="-5 means every hour of the day is 5 °C colder than it really was.")
    make_holiday = col3.checkbox("Treat as a bank holiday")

    # a future day has no real demand yet: only the forecast is shown
    future = live and pd.Timestamp(day) > last_real_day
    if future:
        predict = predict_future_day
        days_after = (pd.Timestamp(day) - last_real_day).days
        st.info("**Future day: only the forecast is shown.** There is no real demand for this day yet, so there is no "
                "actual line and no error. This day is " + str(days_after) + " day(s) after the last day with real demand. "
                "The temperature is the weather forecast.")
    else:
        predict = predict_day

    # normal forecast, and the forecast with the user's changes
    normal = predict(data, model, features, day)
    already_holiday = normal["is_holiday"][0] == 1

    if already_holiday:
        st.info("This day is already a UK bank holiday, so the bank holiday box does not change anything.")

    changed = False
    if temperature_change != 0 or make_holiday:
        changed = True
        what_if = predict(data, model, features, day, temperature_change, make_holiday)

    if changed:
        shown = what_if
        label = " (with your changes)"
    else:
        shown = normal
        label = ""

    filled_hours = int(normal["was_filled"].sum())
    if live and not future and filled_hours > 0:
        st.info(str(filled_hours) + " of the 24 hours of real demand on this day were missing in the live data and were filled. "
                "The black line and the error are less exact for these hours.")

    # numbers at the top
    error = (shown["load"] - shown["forecast"]).abs()
    mape = (error / shown["load"]).mean() * 100
    normal_error = (normal["load"] - normal["forecast"]).abs()
    normal_mape = (normal_error / normal["load"]).mean() * 100

    m1, m2, m3, m4 = st.columns(4)
    if future:
        # no real demand, so no error
        if changed:
            m1.metric("Average forecast" + label, str(round(shown["forecast"].mean())) + " MW",
                      delta=str(round(shown["forecast"].mean() - normal["forecast"].mean())) + " MW")
            m2.metric("Peak forecast" + label, str(round(shown["forecast"].max())) + " MW",
                      delta=str(round(shown["forecast"].max() - normal["forecast"].max())) + " MW")
        else:
            m1.metric("Average forecast", str(round(shown["forecast"].mean())) + " MW")
            m2.metric("Peak forecast", str(round(shown["forecast"].max())) + " MW")
        m3.metric("Lowest forecast" + label, str(round(shown["forecast"].min())) + " MW")
        m4.metric("Average temperature" + label, str(round(shown["temperature"].mean() + temperature_change, 1)) + " °C")
    elif changed:
        m1.metric("Average forecast" + label, str(round(shown["forecast"].mean())) + " MW",
                  delta=str(round(shown["forecast"].mean() - normal["forecast"].mean())) + " MW")
        m2.metric("Peak forecast" + label, str(round(shown["forecast"].max())) + " MW",
                  delta=str(round(shown["forecast"].max() - normal["forecast"].max())) + " MW")
        m3.metric("Average error (MAE)" + label, str(round(error.mean())) + " MW",
                  delta=str(round(error.mean() - normal_error.mean())) + " MW", delta_color="inverse",
                  help="On average, how many MW the forecast is away from the real demand on this day.")
        m4.metric("Average error (MAPE)" + label, str(round(mape, 1)) + " %",
                  delta=str(round(mape - normal_mape, 1)) + " %", delta_color="inverse",
                  help="The same error as a percentage of the real demand.")
    else:
        m1.metric("Average forecast", str(round(shown["forecast"].mean())) + " MW")
        m2.metric("Peak forecast", str(round(shown["forecast"].max())) + " MW")
        m3.metric("Average error (MAE)", str(round(error.mean())) + " MW",
                  help="On average, how many MW the forecast is away from the real demand on this day.")
        m4.metric("Average error (MAPE)", str(round(mape, 1)) + " %",
                  help="The same error as a percentage of the real demand.")

    # effect of each change on its own
    if changed:
        if future:
            st.caption("The small numbers under each value show the change compared with the normal forecast.")
        else:
            st.caption("The small numbers under each value show the change compared with the normal forecast. "
                       "The error is measured against the real demand, so changes that do not match the real "
                       "weather usually make the error bigger.")

        effects = "**Effect on the average forecast:**\n\n"
        if temperature_change != 0:
            temperature_only = predict(data, model, features, day, temperature_change, False)
            effect = temperature_only["forecast"].mean() - normal["forecast"].mean()
            effects += "- Temperature " + str(temperature_change) + " °C on its own: **" + str(round(effect)) + " MW**\n"
        if make_holiday and not already_holiday:
            holiday_only = predict(data, model, features, day, 0, True)
            effect = holiday_only["forecast"].mean() - normal["forecast"].mean()
            effects += "- Bank holiday on its own: **" + str(round(effect)) + " MW**\n"
        total = what_if["forecast"].mean() - normal["forecast"].mean()
        effects += "- All your changes together: **" + str(round(total)) + " MW**\n"
        st.success(effects)

        if temperature_change != 0 and make_holiday and not already_holiday:
            st.write("Colder weather raises demand and a bank holiday lowers it, so together they can cancel each other out.")
        if temperature_change != 0 and day.month in [5, 6, 7, 8, 9]:
            st.write("In summer the temperature has only a small effect, because the UK uses very little air conditioning.")

    # chart
    fig = go.Figure()
    if not future:
        fig.add_trace(go.Scatter(x=normal["time"], y=normal["load"], name="Actual", line=dict(color="black", width=3)))
    fig.add_trace(go.Scatter(x=normal["time"], y=normal["forecast"], name="XGBoost forecast"))
    if changed:
        fig.add_trace(go.Scatter(x=what_if["time"], y=what_if["forecast"], name="XGBoost forecast with your changes",
                                 line=dict(dash="dash")))
    title = "Real demand and the XGBoost forecast"
    if future:
        title = "XGBoost forecast (future day, no real demand yet)"
    fig.update_layout(title=title, xaxis_title="Time (UTC)", yaxis_title="Load (MW)", height=450)
    st.plotly_chart(fig, width="stretch")

    # hourly table
    with st.expander("Hourly values"):
        table = pd.DataFrame()
        table["time (UTC)"] = normal["time"].dt.strftime("%H:%M")
        table["temperature (°C)"] = normal["temperature"].round(1)
        if not future:
            table["actual (MW)"] = normal["load"].round()
        table["XGBoost forecast (MW)"] = normal["forecast"].round()
        if changed:
            table["XGBoost forecast with changes (MW)"] = what_if["forecast"].round()
        st.dataframe(table, hide_index=True, width="stretch")

    if future:
        st.caption("XGBoost starts from the real demand up to yesterday and then uses its own forecasts. "
                   "The temperature is the weather forecast.")
    else:
        st.caption("Hour 1 uses the real demand of the hour before. Hours 2-24 use XGBoost's own forecasts, "
                   "as in the evaluation. The temperature is the measured value (like a perfect weather forecast).")
    if live:
        st.caption("Sources of the live data: demand from Elexon (actual total load), temperature from Open-Meteo. "
                   "The download is kept for 3 hours and then done again.")

    with st.expander("Words used on this page"):
        st.markdown(
            "- **Demand (or load)**: how much electricity Great Britain uses in one hour.\n"
            "- **MW (megawatt)**: the unit of demand. 1 MW is 1,000 kilowatts.\n"
            "- **Actual**: the real demand that was measured.\n"
            "- **Forecast**: the demand that XGBoost predicts.\n"
            "- **Average forecast**: the average of the 24 hourly forecasts of the day.\n"
            "- **Peak forecast**: the highest of the 24 hourly forecasts of the day.\n"
            "- **MAE (Mean Absolute Error)**: on average, how many MW the forecast is away from the real demand. Lower is better.\n"
            "- **MAPE (Mean Absolute Percentage Error)**: the same error as a percentage of the real demand. Lower is better.\n"
            "- **Temperature change**: makes every hour of the day warmer or colder than it really was.\n"
            "- **Bank holiday**: a public holiday. People use less electricity on these days.\n"
            "- **Test year 2019**: the year that was kept apart to test the models. Its data is saved in the project.\n"
            "- **Live data**: the newest demand and temperature, downloaded from the internet when you open this option.\n"
            "- **UTC**: the standard world time. In winter it is the same as UK time. In summer UK time is one hour ahead."
        )
