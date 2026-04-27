import os
import streamlit as st
from dotenv import load_dotenv

def load_env_config():
    """Ensures .env is loaded from the absolute project root for local dev."""
    env_path = os.path.join(os.getcwd(), ".env")
    load_dotenv(dotenv_path=env_path)

def get_secret(key, default=""):
    """
    Cloud-Aware Secret Getter.
    Checks Streamlit Secrets first (Production), then os.environ (Local).
    """
    # 1. Try Streamlit Secrets
    try:
        if key in st.secrets:
            val = st.secrets[key]
            # Clean the result (remove quotes/whitespace)
            if isinstance(val, str):
                return val.strip().strip('"').strip("'")
            return val
    except Exception:
        pass

    # 2. Try Environment Variables
    val = os.getenv(key, default)
    
    # Clean the result (remove quotes/whitespace)
    if isinstance(val, str):
        return val.strip().strip('"').strip("'")
    return val
