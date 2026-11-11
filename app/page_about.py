# Page 4: about the research (shows the text of RESEARCH_QA.md)

import streamlit as st

from data_loader import load_about_text


def show():
    st.markdown(load_about_text())
