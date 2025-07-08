import streamlit as st
from file_uploads import upload_zip_file, upload_github_repo, upload_local_directory
from datetime import datetime
from styles import apply_main_styles, apply_radio_pill_styles

st.set_page_config(
    page_title="Python Code Analyzer",
    page_icon="🐍",
    layout="centered",
)

# Apply main styles
st.markdown(apply_main_styles(), unsafe_allow_html=True)

st.markdown("<p class='big-font'>🐍 Python Code Analyzer</p>", unsafe_allow_html=True)

st.write(
    "Analyze, explore, and understand any Python codebase. Upload a ZIP archive, clone a GitHub repo, or point to a local folder — we’ll parse the project and build an interactive graph for you."
)


st.caption(f"Session started {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# ── Sleek horizontal radio selector ─────────────────────────────────

st.markdown("### 🚀 Choose your ingestion method")

# Apply radio button pill-style CSS
st.markdown(apply_radio_pill_styles(), unsafe_allow_html=True)

upload_method = st.radio(
    label="",  # we add our own header above
    options=[
        "📦 ZIP archive",
        "🐙 GitHub repository",
        "💻 Local directory",
    ],
    horizontal=True,
)

# Map selection to corresponding action
if "ZIP" in upload_method:
    st.info("**Tip:** Compress your project folder into a `.zip` and upload it here.")
    upload_zip_file()

elif "GitHub" in upload_method:
    st.info("**Tip:** Paste a public GitHub URL like `https://github.com/username/repo`. Private repos require proper SSH or token setup (not yet supported).")
    upload_github_repo()

else:  # Local directory
    st.info("**Tip:** Enter an absolute path on this machine where the Streamlit app is running.")
    upload_local_directory()
