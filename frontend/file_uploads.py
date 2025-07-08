import streamlit as st
import os
from file_processing import copy_local_dir, reset_dir
import sys
from pathlib import Path
import subprocess
import zipfile

# ── ensure project root is in Python path ───────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
    
from pipeline import ingestion_pipeline

def upload_zip_file():
    
    uploaded_file = st.file_uploader("Upload your ZIP file here", type=["zip"])

    if uploaded_file is None:
        st.warning("⚠️ Please upload a ZIP file.")
        return  
    
    save_dir = Path("/tmp/uploaded_zips")
    save_dir.mkdir(parents=True, exist_ok=True)
    save_path = save_dir / uploaded_file.name

    with open(save_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    st.success(f"✅ Successfully uploaded {uploaded_file.name}")

    
    extract_dir = save_dir / (save_path.stem + "_unzipped")
    if extract_dir.exists():
        reset_dir(extract_dir, empty_ok=True)  
    extract_dir.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(save_path, "r") as zip_ref:
        zip_ref.extractall(extract_dir)

    
    dest_dir = PROJECT_ROOT / "testing"
    copy_local_dir(str(extract_dir), str(dest_dir))

    st.session_state["start_parsing"] = True
    with st.spinner("Parsing the codebase…"):
        ingestion_pipeline([str(dest_dir)], "py")
    st.session_state["start_parsing"] = False

    st.success("✅ Codebase parsed successfully")
    
def upload_github_repo():
   
    repo_link = st.text_input("Enter your GitHub repository URL")

    
    if not st.button("Clone & Analyze", disabled=not repo_link):
        return
    
    if not repo_link.startswith("https://github.com/"):
        st.warning("⚠️ Please enter a valid public GitHub repository URL.")
        return

    clone_dir = PROJECT_ROOT / "testing"

    try:
        reset_dir(str(clone_dir))
    except Exception as exc:
        st.error(f"❌ Could not prepare destination folder: {exc}")
        return
    with st.spinner("Cloning repository…"):
        result = subprocess.run([
            "git",
            "clone",
            "--depth",
            "1",  
            repo_link,
            str(clone_dir),
        ], capture_output=True, text=True)

    if result.returncode != 0:
        st.error("❌ Git clone failed:\n" + result.stderr)
        return
    
    with st.spinner("Parsing the codebase…"):
        ingestion_pipeline([str(clone_dir)], "py")

    st.success("✅ Codebase parsed successfully")


def upload_local_directory():
    
    dir_path = st.text_input("Enter the path of the local directory:")

    if not st.button("Analyze", disabled=not dir_path):
        return

    if not dir_path or not os.path.isdir(dir_path):
        st.error(f"❌ The path `{dir_path}` is not a valid directory.")
        return

    src_dir = dir_path.strip()
    dest_dir = PROJECT_ROOT / "testing"

    try:
        reset_dir(str(dest_dir))
    except Exception as exc:
        st.error(f"❌ Could not prepare destination folder: {exc}")
        return

    try:
        copy_local_dir(src_dir, str(dest_dir))
    except Exception as exc:
        st.error(f"❌ Copy failed: {exc}")
        return

    with st.spinner("Parsing the codebase…"):
        ingestion_pipeline([str(dest_dir)], "py")

    st.success("✅ Codebase parsed successfully")
                
        
           
    
    
    