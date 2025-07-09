import streamlit as st
from modules.frontend.analytics import show_analytics

st.set_page_config(page_title="Basic Analytics Dashboard", page_icon="✅", layout="wide")
st.title("📊 Codebase Analytics Dashboard")

st.write("This is the analytics dashboard")

if st.session_state.get("parsing_complete", False):
    show_analytics()
else:
    st.info("Run the analysis from the Home page first, then return here to view the dashboard.")