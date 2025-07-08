import streamlit as st
from frontend.analytics import show_analytics

st.set_page_config(page_title="Test", page_icon="✅")
st.title("📊 Codebase Analytics Dashboard")

st.write("This is the analytics dashboard")

show_analytics()