# Page 2: the saved 2019 forecasts of all five models on one day

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from data_loader import load_saved_forecasts, model_names
from tables import markdown_table


def show():
    st.title("Compare models")
    st.write("The saved 2019 forecasts of all five models (notebooks 05-07). Choose a day to see how close each model was.")

    saved = load_saved_forecasts()

    col1, col2 = st.columns([1, 3])
    compare_day = col1.date_input("Day", value=pd.Timestamp("2019-02-06"),
                                  min_value=pd.Timestamp("2019-01-01"), max_value=pd.Timestamp("2019-12-31"))
    chosen = col2.multiselect("Models", model_names, default=model_names)

    start = pd.Timestamp(compare_day)
    one_day = saved[(saved["time"] >= start) & (saved["time"] < start + pd.Timedelta(hours=24))]

    # chart
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=one_day["time"], y=one_day["actual"], name="Actual", line=dict(color="black", width=3)))
    for name in chosen:
        fig.add_trace(go.Scatter(x=one_day["time"], y=one_day[name], name=name))
    fig.update_layout(title="Actual demand and forecasts", xaxis_title="Time (UTC)", yaxis_title="Load (MW)", height=450)
    st.plotly_chart(fig, width="stretch")

    # error of each model on this day
    rows = []
    for name in chosen:
        day_mae = (one_day["actual"] - one_day[name]).abs().mean()
        rows.append([name, round(day_mae)])
    day_errors = pd.DataFrame(rows, columns=["Model", "MAE on this day (MW)"])
    day_errors = day_errors.sort_values("MAE on this day (MW)").reset_index(drop=True)

    st.subheader("Error on this day")
    st.markdown(markdown_table(day_errors, bold_row=0))
    st.caption("Lower is better. The best model on this day is in bold.")

    st.info(
        "**Why is the best model here not always XGBoost?**\n\n"
        "This table is about **one day** only. On one day, any model can be the best.\n\n"
        "XGBoost is the best model **on average over the whole test year 2019** (see the Results page). "
        "It does not win every day:\n\n"
        "| Model | Days it was the best (out of 365) |\n"
        "|---|---|\n"
        "| XGBoost | 109 |\n"
        "| LSTM | 87 |\n"
        "| PatchTST | 84 |\n"
        "| SARIMA | 51 |\n"
        "| Seasonal naive | 34 |\n\n"
        "For example, choose 22 April 2019. It is Easter Monday, a bank holiday. "
        "On bank holidays LSTM has a slightly lower error than XGBoost."
    )
