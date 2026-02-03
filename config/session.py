import streamlit as st
import os

def initialize_session_state():
    defaults = {
        "api_key": os.getenv("BRIA_API_KEY"),
        "generated_images": [],
        "current_image": None,
        "pending_urls": [],
        "edited_image": None,
        "original_prompt": "",
        "enhanced_prompt": None,
    }

    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v
