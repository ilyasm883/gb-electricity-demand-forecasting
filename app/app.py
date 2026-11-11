# Main file of the web app for the GB electricity demand forecasting project.
# It sets up the page and the sidebar menu, then shows the page the user chooses.
#
# Run it from the implementation folder:  streamlit run app/app.py

import streamlit as st

from data_loader import load_data, load_model
import page_prediction
import page_compare
import page_results
import page_about

st.set_page_config(page_title="GB Electricity Demand Forecasting", layout="wide")

data = load_data()
model, features = load_model()

# sidebar with the page menu
st.sidebar.title("GB Demand Forecasting")
page = st.sidebar.radio("Page", ["Prediction", "Compare models", "Results", "About"])
st.sidebar.write("Hourly electricity demand forecasting for Great Britain with five models.")
st.sidebar.write("Data: Open Power System Data, 2015-2019")
st.sidebar.write("Train: 2015-2017, validation: 2018, test: 2019")
st.sidebar.warning("Academic prototype (COM748 MSc project). Not a tool for real grid operation.")

# show the chosen page
if page == "Prediction":
    page_prediction.show(data, model, features)
elif page == "Compare models":
    page_compare.show()
elif page == "Results":
    page_results.show(model, features)
elif page == "About":
    page_about.show()
