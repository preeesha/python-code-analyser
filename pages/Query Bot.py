import streamlit as st
from modules.frontend.styles import apply_main_styles


st.set_page_config(page_title="Query Bot", page_icon="🤖", layout="wide")
st.markdown(apply_main_styles(), unsafe_allow_html=True)
st.title("🤖 Codebase Query Bot")


st.markdown("### Ask questions about your codebase")
st.markdown("*Ask natural language questions about your Python code structure, functions, classes, and relationships.*")


if not st.session_state.get("parsing_complete", False):
    st.warning("⚠️ **No codebase data found.** Please run the analysis from the Home page first.")
    st.info("💡 Once you've uploaded and analyzed your codebase, return here to ask questions about it.")
else:
    
    with st.container():
        col1, col2 = st.columns([4, 1])
        
        with col1:
            user_query = st.text_input(
                "Your Question:",
                placeholder="e.g., 'Show me all functions that call the login method' or 'What classes inherit from BaseModel?'",
                help="Ask questions about functions, classes, imports, relationships, or any code structure in your project."
            )
        
        with col2:
            st.markdown("<br>", unsafe_allow_html=True) 
            submit_query = st.button("🚀 Ask", use_container_width=True)
    
    
    with st.expander("💡 Example Questions"):
        st.markdown("""
        - **Functions & Methods:** "Show me all functions that call the database connection method"
        - **Classes & Inheritance:** "What classes inherit from the BaseModel class?"
        - **Imports & Dependencies:** "Which modules import the requests library?"
        - **Code Structure:** "Show me the relationship between User and Profile classes"
        - **File Analysis:** "What functions are defined in the utils module?"
        - **Complex Queries:** "Find all methods that access the user_id variable"
        """)
    
   
st.markdown("---")
st.markdown("*💡 **Tips:** Ask specific questions about your code structure. The more detailed your question, the better the results!*")
