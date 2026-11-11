# Page 1: live 24-hour forecast with XGBoost, with temperature and bank holiday "what if" controls

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from predictor import predict_day


def show(data, model, features):
    st.title("Prediction")
    st.subheader("Forecast one day with XGBoost (the best model)")

    st.info(
        "**How the forecast works**\n\n"
        "1. You choose a day in 2019.\n"
        "2. The model looks at the real demand of the week before that day.\n"
        "3. It also uses the hour, day of the week, month, bank holiday and temperature of each hour.\n"
        "4. It forecasts the demand for each of the 24 hours of that day.\n"
        "5. The black line shows the real demand, so you can see how close the forecast is.\n\n"
        "**Try it:** change the temperature or mark the day as a bank holiday. The model makes a new forecast "
        "and the numbers below show how much it changed."
    )

    # user choices
    col1, col2, col3 = st.columns(3)
    day = col1.date_input("Day to forecast", value=pd.Timestamp("2019-02-06"),
                          min_value=pd.Timestamp("2019-01-01"), max_value=pd.Timestamp("2019-12-31"))
    temperature_change = col2.slider("Temperature change (°C)", -10, 10, 0,
                                     help="-5 means every hour of the day is 5 °C colder than it really was.")
    make_holiday = col3.checkbox("Treat as a bank holiday")

    # normal forecast, and the forecast with the user's changes
    normal = predict_day(data, model, features, day)
    already_holiday = normal["is_holiday"][0] == 1

    if already_holiday:
        st.info("This day is already a UK bank holiday, so the bank holiday box does not change anything.")

    changed = False
    if temperature_change != 0 or make_holiday:
        changed = True
        what_if = predict_day(data, model, features, day, temperature_change, make_holiday)

    if changed:
        shown = what_if
        label = " (with your changes)"
    else:
        shown = normal
        label = ""

    # numbers at the top
    error = (shown["load"] - shown["forecast"]).abs()
    mape = (error / shown["load"]).mean() * 100
    normal_error = (normal["load"] - normal["forecast"]).abs()
    normal_mape = (normal_error / normal["load"]).mean() * 100

    m1, m2, m3, m4 = st.columns(4)
    if changed:
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
        st.caption("The small numbers under each value show the change compared with the normal forecast. "
                   "The error is measured against the real demand, so changes that do not match the real "
                   "weather usually make the error bigger.")

        effects = "**Effect on the average forecast:**\n\n"
        if temperature_change != 0:
            temperature_only = predict_day(data, model, features, day, temperature_change, False)
            effect = temperature_only["forecast"].mean() - normal["forecast"].mean()
            effects += "- Temperature " + str(temperature_change) + " °C on its own: **" + str(round(effect)) + " MW**\n"
        if make_holiday and not already_holiday:
            holiday_only = predict_day(data, model, features, day, 0, True)
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
    fig.add_trace(go.Scatter(x=normal["time"], y=normal["load"], name="Actual", line=dict(color="black", width=3)))
    fig.add_trace(go.Scatter(x=normal["time"], y=normal["forecast"], name="Normal forecast"))
    if changed:
        fig.add_trace(go.Scatter(x=what_if["time"], y=what_if["forecast"], name="Forecast with your changes",
                                 line=dict(dash="dash")))
    fig.update_layout(title="Actual and forecast demand", xaxis_title="Time (UTC)", yaxis_title="Load (MW)", height=450)
    st.plotly_chart(fig, width="stretch")

    # hourly table
    with st.expander("Hourly values"):
        table = pd.DataFrame()
        table["time (UTC)"] = normal["time"].dt.strftime("%H:%M")
        table["temperature (°C)"] = normal["temperature"].round(1)
        table["actual (MW)"] = normal["load"].round()
        table["normal forecast (MW)"] = normal["forecast"].round()
        if changed:
            table["forecast with changes (MW)"] = what_if["forecast"].round()
        st.dataframe(table, hide_index=True, width="stretch")

    st.caption("Hour 1 uses the real demand of the hour before. Hours 2-24 use the model's own forecasts, "
               "as in the evaluation. The temperature is the measured value (like a perfect weather forecast).")
