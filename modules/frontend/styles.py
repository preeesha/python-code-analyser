
LANDING_PAGE_CONTENT = """
Welcome to the Python Code Analyzer! This tool helps you explore, understand, and visualize any Python codebase.

- **See the bigger picture:** Uncover high-level architecture and component interactions.
- **Drill down into details:** Analyze dependencies, function calls, and data structures.
- **Identify complexity:** Find complex files and functions that might need refactoring.

Ready to start? Click the button below to begin analyzing your project.
""" 
# Main app styling
MAIN_STYLES = """
<style>

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    .stApp {
        background-color: #121212;
        color: #e6e6e6;
    }

    .big-font {
        font-size: 34px !important;
        font-weight: 800;
        background: linear-gradient(90deg, #ff8a00, #e52e71, #9b00ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .stButton>button {
        background: linear-gradient(135deg, #ff0080 0%, #7928ca 100%);
        color: #ffffff;
        border: none;
        padding: 0.6rem 1.2rem;
        font-weight: 600;
        border-radius: 8px;
        transition: 0.3s ease-in-out;
    }
    .stButton>button:hover {
        transform: scale(1.05);
        box-shadow: 0 0 10px rgba(255, 0, 128, 0.7);
        transition: 0.3s ease-in-out;
        cursor: pointer;
    }

    /* Radio label color */
    label[data-baseweb="radio"] span {
        color: #e0e0e0 !important;
    }
</style>
"""

# Radio button pill-style styling
RADIO_PILL_STYLES = """
<style>
    div[data-baseweb="radio"] > div {
        flex-direction: row !important;
    }
    div[data-baseweb="radio"] label {
        background: rgba(255,255,255,0.07);
        padding: 0.4rem 1rem;
        margin-right: 0.5rem;
        border-radius: 999px;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    div[data-baseweb="radio"] label:hover {
        background: rgba(255,255,255,0.15);
    }
    div[data-baseweb="radio"] input:checked + div>div {
        background: linear-gradient(135deg, #ff0080 0%, #7928ca 100%);
        box-shadow: 0 0 8px rgba(255,0,128,0.6);
    }
</style>
"""

def apply_main_styles():
    """Apply the main application styles."""
    return MAIN_STYLES

def apply_radio_pill_styles():
    """Apply the radio button pill-style styles."""
    return RADIO_PILL_STYLES 