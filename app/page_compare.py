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
    compare_day = col1.date_input("Day", value=pd.Timestamp("2019-04-22"),
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
