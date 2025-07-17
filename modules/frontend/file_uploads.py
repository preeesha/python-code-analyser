import streamlit as st
import os
from modules.frontend.file_processing import copy_local_dir, reset_dir
import sys
from pathlib import Path
import subprocess
import zipfile

# ── ensure project root is in Python path ───────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
    
from modules.ingesion_pipeline import ingestion_pipeline

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
    st.session_state["parsing_complete"] = True
    
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
    st.session_state["parsing_complete"] = True


def upload_local_directory():
    
    st.markdown("**Upload your entire project directory:**")
    st.info("💡 **Tip**: Select all files from your project directory (including subdirectories). Most browsers allow you to select entire folder contents by selecting all files (Ctrl+A / Cmd+A) after opening a folder.")
    
    uploaded_files = st.file_uploader(
        "Browse and select ALL files from your project directory",
        accept_multiple_files=True,
        help="Select all files from your project directory. This will preserve the directory structure. Python files (.py) will be automatically identified for analysis."
    )

    if not uploaded_files:
        st.warning("⚠️ Please select files from your project directory.")
        return

    # Show file count and Python file count
    python_files = [f for f in uploaded_files if f.name.endswith('.py')]
    st.info(f"📁 Selected {len(uploaded_files)} total files, {len(python_files)} Python files found")
    
    if len(python_files) == 0:
        st.warning("⚠️ No Python files found in the selected files. Please make sure to include .py files.")
        return

    if not st.button("Analyze Project Directory", disabled=not uploaded_files):
        return

    dest_dir = PROJECT_ROOT / "testing"

    try:
        reset_dir(str(dest_dir))
    except Exception as exc:
        st.error(f"❌ Could not prepare destination folder: {exc}")
        return

    # Create destination directory structure and save uploaded files
    try:
        dest_dir.mkdir(parents=True, exist_ok=True)
        
        # Save all uploaded files preserving directory structure
        for uploaded_file in uploaded_files:
            # Handle file paths that might contain directory separators
            # Some browsers preserve relative paths in file.name
            relative_path = uploaded_file.name.replace('\\', '/')  # Normalize path separators
            file_path = dest_dir / relative_path
            
            # Create parent directories if they don't exist
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
        
        st.success(f"✅ Successfully uploaded {len(uploaded_files)} files ({len(python_files)} Python files)")
        
        # Show the directory structure created
        with st.expander("📂 View uploaded directory structure"):
            for uploaded_file in sorted(uploaded_files, key=lambda x: x.name):
                icon = "🐍" if uploaded_file.name.endswith('.py') else "📄"
                st.text(f"{icon} {uploaded_file.name}")
        
    except Exception as exc:
        st.error(f"❌ File upload failed: {exc}")
        return

    with st.spinner("Parsing the codebase…"):
        ingestion_pipeline([str(dest_dir)], "py")

    st.success("✅ Codebase parsed successfully")
    st.session_state["parsing_complete"] = True
                
        
           
    
    
    