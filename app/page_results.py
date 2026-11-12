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
            "Every model forecasts each day of the test year **2019**, for the next 24 hours. "
            "Then we compare the forecasts with the real demand.\n\n"
            "This page uses four error measures. For MAE, RMSE and MAPE, **lower is better**. For skill, **higher is better**.\n\n"
            "- **MAE (Mean Absolute Error)**: on average, how many MW the forecast is wrong by. "
            "Example: MAE = 1,000 MW means the forecast is on average 1,000 MW too high or too low.\n"
            "- **RMSE (Root Mean Squared Error)**: also an average error in MW, but big mistakes count more. "
            "If RMSE is much bigger than MAE, the model sometimes makes very large mistakes.\n"
            "- **MAPE (Mean Absolute Percentage Error)**: the average error as a percentage of the real demand.\n"
            "- **Skill vs seasonal naive**: how much smaller the MAE is compared with the simplest model "
            "(the demand at the same hour last week). 0% means no better, higher is better.\n\n"
            "All the words used on this page are explained at the bottom of the page."
        )

    show_rq1()
    show_rq2()
    show_rq3()
    show_rq4(model, features)
    show_words()


# RQ1: overall accuracy
def show_rq1():
    st.header("RQ1: Which model is most accurate?")
    st.write("This table shows the error of each model over the whole year 2019. The best model is first and in bold.")

    summary = load_table("08_overall_results.csv")
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

    st.caption("Rank = position of the model, 1 is the best. MAE and RMSE are in MW, MAPE and skill are in percent.")

    best = summary["model"][0]
    st.success("**Best model: " + best + "**. It has the lowest error on every measure: on average it is "
               + str(round(summary["MAE"][0])) + " MW (" + str(round(summary["MAPE"][0], 1))
               + "%) away from the real demand, which is " + str(round(summary["skill_vs_naive_%"][0]))
               + "% better than the seasonal naive model.")


# RQ2: error by forecast horizon
def show_rq2():
    st.header("RQ2: How does the error change when we forecast further ahead?")
    st.write("**Horizon** means how many hours ahead the forecast is. Horizon 1 is the next hour. Horizon 24 is one day ahead. "
             "A forecast further ahead is usually harder, so the error is usually bigger.")

    by_horizon = load_table("08_mae_by_horizon.csv")
    fig = go.Figure()
    for name in model_names:
        fig.add_trace(go.Scatter(x=by_horizon["horizon"], y=by_horizon[name], name=name, mode="lines+markers"))
    fig.update_layout(title="MAE for each hour ahead", xaxis_title="Hours ahead (horizon)", yaxis_title="MAE (MW)", height=420)
    st.plotly_chart(fig, width="stretch")
    st.caption("How to read the chart: each line is one model. A lower line means a smaller error.")

    h1_vs_h24 = load_table("08_h1_vs_h24.csv")
    rq2 = pd.DataFrame()
    rq2["Model"] = h1_vs_h24["model"]
    rq2["MAPE 1 hour ahead (%)"] = h1_vs_h24["MAPE_1h"].round(2)
    rq2["MAPE 24 hours ahead (%)"] = h1_vs_h24["MAPE_24h"].round(2)
    rq2["Change (points)"] = h1_vs_h24["increase"].round(2)
    st.dataframe(rq2, hide_index=True, width="stretch")
    st.caption("Change (points) = MAPE 24 hours ahead minus MAPE 1 hour ahead. A positive number means the model gets worse "
               "when it forecasts further ahead. "
               "Every forecast starts at midnight UTC, so the horizon is also the time of day. "
               "SARIMA is best 1 hour ahead, XGBoost is best 24 hours ahead.")

    st.subheader("Is one model really better than another? (Diebold-Mariano test)")
    st.write("Two models can have different errors just by luck. The Diebold-Mariano test checks if the difference is real. "
             "Each row of the table compares two models, Model A and Model B, at one horizon.")
    dm = load_table("08_diebold_mariano.csv")
    dm.columns = ["Horizon (hours)", "Model A", "Model B", "DM statistic", "p-value", "Better model"]
    st.dataframe(dm, hide_index=True, width="stretch")
    st.markdown(
        "**What the columns mean**\n\n"
        "- **Horizon (hours)**: how many hours ahead the two models are compared (1 or 24).\n"
        "- **DM statistic**: the result of the test. A negative number means Model A has the smaller error. "
        "A positive number means Model B has the smaller error. The further from 0, the clearer the difference.\n"
        "- **p-value**: the chance that the difference is only luck. It goes from 0 to 1. "
        "If it is **below 0.05**, the difference is real (we say it is \"significant\").\n"
        "- **Better model**: the model with the smaller error, if the difference is real. "
        "\"no significant difference\" means the two models are equally good."
    )


# RQ3: errors by type of day, peak hours and month
def show_rq3():
    st.header("RQ3: When do the models make their biggest mistakes?")
    st.write("These tables show the MAE (in MW) for different kinds of days and hours. The best model in each row is in bold.")

    day_type = load_table("09_mae_by_day_type.csv")
    period = load_table("09_mae_by_period.csv")
    st.markdown(best_in_row_table(day_type, "Type of day", model_names))
    st.markdown(best_in_row_table(period, "Period", model_names))
    st.markdown(
        "**What the words mean**\n\n"
        "- **holiday**: a bank holiday (public holiday). **weekday**: Monday to Friday. **weekend**: Saturday and Sunday.\n"
        "- **peak**: the busy evening hours, 16:00 to 19:59 UK time. **off-peak**: all other hours.\n"
        "- **Hours**: how many hours of 2019 are in that row."
    )

    fig = go.Figure()
    for name in model_names:
        fig.add_trace(go.Bar(x=day_type["day_type"], y=day_type[name], name=name))
    fig.update_layout(title="MAE by type of day", barmode="group", yaxis_title="MAE (MW)", height=400)
    st.plotly_chart(fig, width="stretch")

    by_month = load_table("09_mae_by_month.csv")
    fig = go.Figure()
    for name in model_names:
        fig.add_trace(go.Scatter(x=by_month["month"], y=by_month[name], name=name, mode="lines+markers"))
    fig.update_layout(title="MAE by month (2019)", xaxis_title="Month (1 = January, 12 = December)", yaxis_title="MAE (MW)", height=400)
    st.plotly_chart(fig, width="stretch")
    st.caption("Bank holidays are the hardest days. The models that do not know about holidays (seasonal naive, PatchTST) "
               "make the biggest mistakes on these days.")


# RQ4: feature ablation and feature importance
def show_rq4(model, features):
    st.header("RQ4: Do calendar and temperature information help?")
    st.write("A **feature** is a piece of information we give to a model. To see which features help, we trained XGBoost and LSTM "
             "four times, each time with a different set of features. This kind of test is called an **ablation**. "
             "It was done on the validation year 2018.")
    st.markdown(
        "- **A: history only**: only the past demand.\n"
        "- **B: + calendar**: A plus the hour, day of the week, month, weekend and bank holiday.\n"
        "- **C: + temperature**: A plus the temperature.\n"
        "- **D: all**: A plus calendar plus temperature."
    )

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
    fig.update_layout(title="Error with each set of features (2018)", barmode="group", yaxis_title="MAE (MW)", height=350)
    col2.plotly_chart(fig, width="stretch")
    st.caption("Change (%) = how much the MAE changed compared with set A. A negative number means the error went down, which is good.")
    st.success("Using **all features** (set D) gives the lowest error for both models. Calendar features help the most.")

    st.subheader("Which features does XGBoost use most?")
    importance = pd.DataFrame()
    importance["feature"] = features
    importance["importance"] = model.feature_importances_
    importance = importance.sort_values("importance")
    fig = go.Figure(go.Bar(x=importance["importance"], y=importance["feature"], orientation="h"))
    fig.update_layout(title="XGBoost feature importance", xaxis_title="Importance", height=420)
    st.plotly_chart(fig, width="stretch")
    st.markdown(
        "**What the words mean**\n\n"
        "- **Importance**: how much a feature helps XGBoost to make its forecast. A longer bar means the feature is more useful. "
        "All the bars together add up to 1.\n"
        "- **lag1**: the demand 1 hour before. **lag24**: the demand at the same hour yesterday. "
        "**lag168**: the demand at the same hour last week.\n"
        "- **rolling_mean_lag1_window_size24**: the average demand of the last 24 hours. "
        "**rolling_mean_lag1_window_size168**: the average demand of the last week.\n"
        "- **is_weekend**: 1 on Saturday and Sunday. **is_holiday**: 1 on a bank holiday."
    )


# all the words used on this page, in one place
def show_words():
    st.header("Words used on this page")

    st.subheader("General words")
    st.markdown(
        "| Word | What it means |\n"
        "|---|---|\n"
        "| Demand (or load) | How much electricity Great Britain uses in one hour |\n"
        "| MW (megawatt) | The unit of demand. 1 MW is 1,000 kilowatts |\n"
        "| Forecast | The demand that a model predicts |\n"
        "| Actual | The real demand that was measured |\n"
        "| Error | The difference between the forecast and the real demand |\n"
        "| Horizon | How many hours ahead the forecast is (1 = next hour, 24 = one day ahead) |\n"
        "| Test year | 2019. The models never saw this year while learning. All results on this page are for 2019, except RQ4 |\n"
        "| Validation year | 2018. It was used to choose the settings of the models and for the feature test in RQ4 |\n"
        "| Feature | A piece of information we give to a model, for example the hour or the temperature |\n"
        "| Rank | The position of a model. Rank 1 is the best model |\n"
    )

    st.subheader("Error measures")
    st.markdown(
        "| Word | What it means | Good value |\n"
        "|---|---|---|\n"
        "| MAE (Mean Absolute Error) | The average error in MW | Low |\n"
        "| RMSE (Root Mean Squared Error) | Like MAE, but big mistakes count more | Low |\n"
        "| MAPE (Mean Absolute Percentage Error) | The average error as a percentage of the real demand | Low |\n"
        "| Skill vs seasonal naive | How much better a model is than the simplest model, in percent | High |\n"
        "| Change (points) | MAPE 24 hours ahead minus MAPE 1 hour ahead | Close to 0 |\n"
        "| Change (%) | How much the MAE changed compared with feature set A | Negative |\n"
    )

    st.subheader("Diebold-Mariano test")
    st.markdown(
        "| Word | What it means |\n"
        "|---|---|\n"
        "| Diebold-Mariano test | A test that checks if two models really have different errors, or if it is only luck |\n"
        "| DM statistic | The result of the test. Negative: Model A is better. Positive: Model B is better |\n"
        "| p-value | The chance that the difference is only luck. Below 0.05 means the difference is real |\n"
        "| Significant | The difference is real, not luck (p-value below 0.05) |\n"
    )

    st.subheader("The five models")
    st.markdown(
        "| Model | What it is |\n"
        "|---|---|\n"
        "| Seasonal naive | The simplest model. Its forecast is the demand at the same hour last week |\n"
        "| SARIMA | A classic statistics model. It only uses the past demand |\n"
        "| XGBoost | A machine learning model made of many small decision trees. It uses all the features |\n"
        "| LSTM | A deep learning model with a memory. It uses the last week of demand, the calendar and the temperature |\n"
        "| PatchTST | A new deep learning model (a transformer). It only uses the last week of demand |\n"
    )
