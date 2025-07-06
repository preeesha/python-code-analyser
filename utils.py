import json, time
import streamlit as st

def load_json_file(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json_file(data, file_path):
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    


message_types = {
    "info": st.info,
    "warning": st.warning,
    "success": st.success,
    "error": st.error
}

def display_message(message, type_, delay=1.5, rerun=True):
    message_func = message_types.get(type_, "info")
    message_func(message)
    time.sleep(delay)
    if rerun: st.rerun()
    