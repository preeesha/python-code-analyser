import streamlit as st
from file_uploads import upload_zip_file, upload_github_repo, upload_local_directory

st.header("Python Code Analyzer")
st.write(
    "Hey,There this is a python code analyzer that helps you to analyze your pyhton files and helps you in decoding the codebase you are working with ."
)

st.write(
    "So you can choose different ways how you want to upload your files for analysis , upload directly from device or give ur github repository "
)
file_upload_option = st.radio(
    "How would you like to uplaod your project?",
    ["Upload zip file", "Github repository", "local files form system"],
)

if file_upload_option == "Upload zip file":
    upload_zip_file()

elif file_upload_option == "Github repository":
    upload_github_repo()
    
elif file_upload_option == "local files form system":
    upload_local_directory()
