from dotenv import load_dotenv
import streamlit as st

from config.session import initialize_session_state

from components.main_sidebar import sidebar
from tabs import fill, generate, lifestyle, erase

def main():
    
    load_dotenv()
    st.set_page_config(
        page_title="Photo Studio",
        page_icon="🎨",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    st.title("Photo Studio")
    initialize_session_state()
    
    # Sidebar for API key
    sidebar()

    # Main tabs
    tabs = st.tabs([
        "🎨 Generate Image",
        "🖼️ Lifestyle Shot",
        "🎨 Generative Fill",
        "🎨 Erase Elements"
    ])
    # Generate Images Tab
    with tabs[0]:
        generate.render()
    # Product Photography Tab
    with tabs[1]:
        lifestyle.render()
    # Generative Fill Tab
    with tabs[2]:
        fill.render()
    # Erase Elements Tab
    with tabs[3]:
        erase.render()

if __name__ == "__main__":
    main() 