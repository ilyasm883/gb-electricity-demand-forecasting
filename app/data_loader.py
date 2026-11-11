# Reads the data, the saved XGBoost model and the saved forecasts.
# Streamlit keeps them in memory (cache), so each file is only read once.

import pandas as pd
import streamlit as st
from xgboost import XGBRegressor

data_file = "datasets/processed/gb_features_2015_2019.csv"
forecast_folder = "results/forecasts"
tables_folder = "results/tables"
models_folder = "results/models"
about_file = "RESEARCH_QA.md"

# the five models and the file with their 2019 forecasts
model_files = {
    "Seasonal naive": "seasonal_naive.csv",
    "SARIMA": "sarima.csv",
    "XGBoost": "xgboost.csv",
    "LSTM": "lstm.csv",
    "PatchTST": "patchtst.csv",
}
model_names = list(model_files.keys())


@st.cache_data
def load_data():
    data = pd.read_csv(data_file)
    data["time"] = pd.to_datetime(data["time"]).dt.tz_localize(None)
    return data


@st.cache_resource
def load_model():
    model = XGBRegressor()
    model.load_model(models_folder + "/xgboost.json")
    features = pd.read_csv(models_folder + "/xgboost_features.csv")["feature"].tolist()
    return model, features


@st.cache_data
def load_saved_forecasts():
    saved = pd.read_csv(forecast_folder + "/seasonal_naive.csv", parse_dates=["time"])
    saved = saved[["time", "actual"]].copy()
    for name in model_files:
        one = pd.read_csv(forecast_folder + "/" + model_files[name])
        saved[name] = one["forecast"].values
    return saved


def load_table(file_name):
    return pd.read_csv(tables_folder + "/" + file_name)


def load_about_text():
    return open(about_file, encoding="utf-8").read()
