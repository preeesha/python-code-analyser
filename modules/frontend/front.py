import streamlit as st
from modules.frontend.styles import apply_radio_pill_styles
from modules.frontend.file_uploads import upload_zip_file, upload_github_repo, upload_local_directory
from modules.frontend.styles import LANDING_PAGE_CONTENT
import time
from pathlib import Path
from streamlit_autorefresh import st_autorefresh


IMAGE_DIR = Path(__file__).resolve().parent.parent / "images"
image_paths = sorted(
    [str(p) for p in IMAGE_DIR.glob("*") if p.suffix.lower() in {".png", ".jpg", ".jpeg", ".svg"}]
)

def render_landing_page():
    
    if "fade_css_added" not in st.session_state:
        fade_css = """
        <style>
        /* Fade-in animation for images */
        .stImage img {
            opacity: 0;
            animation: fadein 1.2s ease-in-out forwards;
        }
        @keyframes fadein {
            from {opacity: 0;}
            to   {opacity: 1;}
        }
        </style>
        """
        st.markdown(fade_css, unsafe_allow_html=True)
        st.session_state.fade_css_added = True

    # Automatically refresh the landing page every 5 seconds
    st_autorefresh(interval=5000, key="landing_autorefresh")

    st.markdown("<h1 style='text-align: center;'>🐍 Python Code Analyzer</h1>", unsafe_allow_html=True)

    if "image_index" not in st.session_state:
        st.session_state.image_index = 0
        st.session_state.last_refresh = time.time()

    # Show current image
    if image_paths:
        current_index = st.session_state.image_index % len(image_paths)
        try:
            with open(image_paths[current_index], "rb") as img_file:
                img_bytes = img_file.read()
            st.image(img_bytes, use_container_width=True)
        except Exception as e:
            print(f"Error displaying image: {e}")
    

    st.write("Welcome to the Python Code Analyzer — visualize your code like never before!")
   
    if st.button("🚀 Analyze Your Codebase", use_container_width=True):
        st.session_state.view = 'analysis'
        st.rerun()

   
    if image_paths and time.time() - st.session_state.last_refresh >= 5:
        st.session_state.image_index = (st.session_state.image_index + 1) % len(image_paths)
        st.session_state.last_refresh = time.time()

    st.write(LANDING_PAGE_CONTENT)

def render_analysis_page():

    st.markdown("### 🚀 Choose your ingestion method")
    st.markdown(apply_radio_pill_styles(), unsafe_allow_html=True)

    upload_method = st.radio(
        label="Select the source of your Python project:",
        options=["📦 ZIP archive", "🐙 GitHub repository", "💻 Local directory"],
        horizontal=True,
    )

    if "ZIP" in upload_method:
        st.info("**Tip:** Compress your project folder into a `.zip` and upload it here.")
        upload_zip_file()
    elif "GitHub" in upload_method:
        st.info("**Tip:** Paste a public GitHub URL. Private repos are not yet supported.")
        upload_github_repo()
    else:
        st.info("**Tip:** Enter the absolute path to a directory on your local machine.")
        upload_local_directory()
    
    if st.session_state.get("parsing_complete", False):
        st.success("Parsing complete! Open the 'Analytics Dashboard' page from the sidebar to explore insights.")