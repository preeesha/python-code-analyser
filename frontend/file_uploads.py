import streamlit as st
import os
from file_processing import copy_local_dir
from pipeline import ingestion_pipeline
import sys
from pathlib import Path

# ── ensure project root is in Python path ───────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

def upload_zip_file():
    uploaded_file = st.file_uploader("upload your zip file here", type=["zip"])
    if uploaded_file is not None:
        st.success(f"✅ Successfully uploaded {uploaded_file.name}")
        st.session_state["zip_file"] = uploaded_file
    
def upload_github_repo():
    repo_link = st.text_input("enter your github repository link ")
    if st.button("submit"):
        if repo_link.startswith("https://github.com/"):
            st.success("✅ successfully uploaded github repository")
            st.session_state["repo_link"] = repo_link
        else:
            st.warning("⚠️ please enter a valid github repository link")
    
    
def upload_local_directory():
    dir_path = st.text_input("enter the path of the local directory:")
    if st.button("Submit"):  
        if dir_path:
            dir_path = dir_path.strip()
            if os.path.isdir(dir_path):
                st.session_state["codebase_path"] = dir_path
                st.session_state["start_parsing"] = True
                dest_dir = PROJECT_ROOT / "testing"
                copy_local_dir(dir_path, dest_dir)
                with st.spinner("parsing the codebase..."):
                    if st.session_state["start_parsing"]:
                        ingestion_pipeline([str(dest_dir)], "py")
                        st.session_state["start_parsing"] = False
                st.success("✅ Codebase parsed successfully")
            else:
                st.error(f"❌ The path `{dir_path}` is not a valid directory.")
        else:
            st.warning("⚠️ Please enter a valid directory path.")
                
        
           
    
    
    