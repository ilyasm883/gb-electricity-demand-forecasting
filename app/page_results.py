# Page 3: tables and charts for the four research questions (RQ1-RQ4)

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from data_loader import load_table, model_names
from tables import markdown_table, best_in_row_table


def show(model, features):
    st.title("Results")

    with st.expander("How to read the results", expanded=True):
        st.markdown(
            "All models forecast every day of the test year **2019**, 24 hours ahead. For every error measure, **lower is better**.\n\n"
            "- **MAE (Mean Absolute Error)**: on average, how many MW the forecast is wrong by. "
            "Example: MAE = 1,000 MW means the forecast is on average 1,000 MW too high or too low.\n"
            "- **RMSE (Root Mean Squared Error)**: also an average error in MW, but big mistakes count more. "
            "If RMSE is much bigger than MAE, the model sometimes makes very large mistakes.\n"
            "- **MAPE (Mean Absolute Percentage Error)**: the average error as a percentage of the real demand.\n"
            "- **Skill vs seasonal naive**: how much smaller the MAE is compared with the simplest model "
            "(the demand at the same hour last week). 0% means no better, higher is better."
        )

    show_rq1()
    show_rq2()
    show_rq3()
    show_rq4(model, features)


# RQ1: overall accuracy
def show_rq1():
    st.header("RQ1: Which model is most accurate?")
    summary = load_table("08_summary.csv")
    summary = summary.sort_values("MAE").reset_index(drop=True)

    rq1 = pd.DataFrame()
    rq1["Rank"] = range(1, len(summary) + 1)
    rq1["Model"] = summary["model"]
    rq1["MAE (MW)"] = summary["MAE"].round().astype(int)
    rq1["RMSE (MW)"] = summary["RMSE"].round().astype(int)
    rq1["MAPE (%)"] = summary["MAPE"].round(2)
    rq1["Skill vs seasonal naive (%)"] = summary["skill_vs_naive_%"].round(1)

    col1, col2 = st.columns(2)
    col1.markdown(markdown_table(rq1, bold_row=0))

    colors = ["#1f77b4"] * len(summary)
    colors[0] = "#2ca02c"
    fig = go.Figure(go.Bar(x=summary["model"], y=summary["MAE"], marker_color=colors,
                           text=summary["MAE"].round().astype(int), textposition="outside"))
    fig.update_layout(title="MAE on 2019 (best model in green)", yaxis_title="MAE (MW)", height=350)
    col2.plotly_chart(fig, width="stretch")

    best = summary["model"][0]
    st.success("**Best model: " + best + "**. It has the lowest error on every measure: on average it is "
               + str(round(summary["MAE"][0])) + " MW (" + str(round(summary["MAPE"][0], 1))
               + "%) away from the real demand, which is " + str(round(summary["skill_vs_naive_%"][0]))
               + "% better than the seasonal naive model.")


# RQ2: error by forecast horizon
def show_rq2():
    st.header("RQ2: How does the error change with the forecast horizon?")
    st.write("Horizon = how many hours ahead the forecast is (1 = next hour, 24 = one day ahead).")

    by_horizon = load_table("08_mae_by_horizon.csv")
    fig = go.Figure()
    for name in model_names:
        fig.add_trace(go.Scatter(x=by_horizon["horizon"], y=by_horizon[name], name=name, mode="lines+markers"))
    fig.update_layout(title="MAE by forecast horizon", xaxis_title="Hours ahead", yaxis_title="MAE (MW)", height=420)
    st.plotly_chart(fig, width="stretch")

    h1_vs_h24 = load_table("08_h1_vs_h24.csv")
    rq2 = pd.DataFrame()
    rq2["Model"] = h1_vs_h24["model"]
    rq2["MAPE 1 hour ahead (%)"] = h1_vs_h24["MAPE_1h"].round(2)
    rq2["MAPE 24 hours ahead (%)"] = h1_vs_h24["MAPE_24h"].round(2)
    rq2["Change (points)"] = h1_vs_h24["increase"].round(2)
    st.dataframe(rq2, hide_index=True, width="stretch")
    st.caption("Forecasts start at midnight UTC, so the horizon is also the time of day. "
               "SARIMA is best 1 hour ahead, XGBoost is best 24 hours ahead.")

    st.subheader("Are the differences real? (Diebold-Mariano test)")
    dm = load_table("08_diebold_mariano.csv")
    dm.columns = ["Horizon (hours)", "Model A", "Model B", "DM statistic", "p-value", "Better model"]
    st.dataframe(dm, hide_index=True, width="stretch")
    st.caption("A p-value below 0.05 means the difference between the two models is significant.")


# RQ3: errors by type of day, peak hours and month
def show_rq3():
    st.header("RQ3: When do the models make their biggest mistakes?")
    st.write("MAE (MW) by type of day and for peak hours (16:00-19:59 UK time). The best model in each row is in bold.")

    day_type = load_table("09_mae_by_day_type.csv")
    period = load_table("09_mae_by_period.csv")
    st.markdown(best_in_row_table(day_type, "Type of day", model_names))
    st.markdown(best_in_row_table(period, "Period", model_names))

    fig = go.Figure()
    for name in model_names:
        fig.add_trace(go.Bar(x=day_type["day_type"], y=day_type[name], name=name))
    fig.update_layout(title="MAE by type of day", barmode="group", yaxis_title="MAE (MW)", height=400)
    st.plotly_chart(fig, width="stretch")

    by_month = load_table("09_mae_by_month.csv")
    fig = go.Figure()
    for name in model_names:
        fig.add_trace(go.Scatter(x=by_month["month"], y=by_month[name], name=name, mode="lines+markers"))
    fig.update_layout(title="MAE by month (2019)", xaxis_title="Month", yaxis_title="MAE (MW)", height=400)
    st.plotly_chart(fig, width="stretch")
    st.caption("Bank holidays are the hardest days. Models without a holiday input (seasonal naive, PatchTST) suffer most.")


# RQ4: feature ablation and feature importance
def show_rq4(model, features):
    st.header("RQ4: Do calendar and temperature features help?")
    st.write("XGBoost and LSTM were trained with four sets of features and tested on the validation year 2018. "
             "A negative change means the error went down compared with set A.")

    ablation = load_table("09_ablation.csv")
    rq4 = pd.DataFrame()
    rq4["Feature set"] = ablation["feature set"]
    rq4["XGBoost MAE (MW)"] = ablation["XGBoost MAE"].round().astype(int)
    rq4["XGBoost change (%)"] = ablation["XGBoost change vs A (%)"].round(1)
    rq4["LSTM MAE (MW)"] = ablation["LSTM MAE"].round().astype(int)
    rq4["LSTM change (%)"] = ablation["LSTM change vs A (%)"].round(1)

    col1, col2 = st.columns(2)
    col1.markdown(markdown_table(rq4, bold_row=ablation["XGBoost MAE"].idxmin()))

    fig = go.Figure()
    fig.add_trace(go.Bar(x=ablation["feature set"], y=ablation["XGBoost MAE"], name="XGBoost"))
    fig.add_trace(go.Bar(x=ablation["feature set"], y=ablation["LSTM MAE"], name="LSTM"))
    fig.update_layout(title="Feature ablation (2018)", barmode="group", yaxis_title="MAE (MW)", height=350)
    col2.plotly_chart(fig, width="stretch")
    st.success("Using **all features** (set D) gives the lowest error for both models. Calendar features help the most.")

    st.subheader("Which features does XGBoost use most?")
    importance = pd.DataFrame()
    importance["feature"] = features
    importance["importance"] = model.feature_importances_
    importance = importance.sort_values("importance")
    fig = go.Figure(go.Bar(x=importance["importance"], y=importance["feature"], orientation="h"))
    fig.update_layout(title="XGBoost feature importance", xaxis_title="Importance", height=420)
    st.plotly_chart(fig, width="stretch")
    st.caption("lag168 = same hour last week, lag1 = 1 hour before, lag24 = same hour yesterday.")
