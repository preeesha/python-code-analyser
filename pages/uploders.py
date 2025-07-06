import os
from utils import display_message
import streamlit as st


def upload_local_directory():
    local_path = st.text_input("Enter the full local directory path:")
    if st.button("Submit Path"):
        if local_path:
            if os.path.isdir(local_path):
                st.session_state["codebase_path"] = local_path
                st.session_state["start_parsing"] = True
                display_message(f"Directory path received: `{local_path}`", "success")
            else:
                display_message(f"The path `{local_path}` is not a valid directory.", "error")
        else:
            display_message("⚠️ Please enter a valid directory path.", "warning")
        
def upload_zip_file():
    uploaded_file = st.file_uploader("Upload your codebase ZIP file", type=["zip"])
    if uploaded_file is not None:
        st.success(f"Uploaded file: `{uploaded_file.name}`")


def upload_github_repo():
    repo_link = st.text_input("Enter the GitHub repository URL:")
    if st.button("Submit Repository"):
        if repo_link.startswith("http"):
            st.success(f"GitHub repository link received: `{repo_link}`")
        else:
            st.warning("Please enter a valid GitHub repository URL.")