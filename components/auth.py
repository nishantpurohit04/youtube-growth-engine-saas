import os
import pyrebase
import streamlit as st

from src.config import get_env_clean

def get_firebase_auth():
    """Initializes Firebase and returns the auth object dynamically."""
    firebase_config = {
        "apiKey": get_env_clean("FIREBASE_API_KEY"),
        "authDomain": get_env_clean("FIREBASE_AUTH_DOMAIN"),
        "projectId": get_env_clean("FIREBASE_PROJECT_ID"),
        "storageBucket": get_env_clean("FIREBASE_STORAGE_BUCKET"),
        "messagingSenderId": get_env_clean("FIREBASE_MESSAGING_SENDER_ID"),
        "appId": get_env_clean("FIREBASE_APP_ID"),
        "databaseURL": get_env_clean("FIREBASE_DATABASE_URL"),
    }
    firebase = pyrebase.initialize_app(firebase_config)
    return firebase.auth()

def sign_up(email, password):
    """Creates a new user in Firebase Auth."""
    try:
        auth = get_firebase_auth()
        user = auth.create_user_with_email_and_password(email, password)
        return {"success": True, "user": user}
    except Exception as e:
        return {"success": False, "error": str(e)}

def sign_in(email, password):
    """Authenticates a user with Firebase Auth."""
    try:
        auth = get_firebase_auth()
        user = auth.sign_in_with_email_and_password(email, password)
        return {"success": True, "user": user}
    except Exception as e:
        err_msg = str(e).lower()
        with open("auth_debug.log", "a") as f:
            f.write(f"Login Error: {err_msg}\n")
        if "invalid-password" in err_msg or "email-not-found" in err_msg or "invalid_login_credentials" in err_msg:
            friendly_error = "❌ Invalid email or password. Please try again."
        elif "user-disabled" in err_msg:
            friendly_error = "🚫 This account has been disabled."
        else:
            friendly_error = "⚠️ An unexpected error occurred. Please try again later."
        return {"success": False, "error": friendly_error}

def sign_out():
    """Clears the user session from Streamlit state."""
    if "user" in st.session_state:
        del st.session_state.user

def render_auth_screen():
    """Renders the login/signup UI and handles authentication."""
    st.markdown("<h2 style='text-align: center;'>🔐 Welcome to Growth Engine</h2>", unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["Login", "Sign Up"])
    
    with tab1:
        with st.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login", use_container_width=True)
            
            if submit:
                if email and password:
                    res = sign_in(email, password)
                    if res["success"]:
                        st.session_state.user = res["user"]
                        st.success("Login successful!")
                        st.rerun()
                    else:
                        st.error(f"Login failed: {res['error']}")
                else:
                    st.warning("Please fill in all fields.")
                    
    with tab2:
        with st.form("signup_form"):
            new_email = st.text_input("Email")
            new_password = st.text_input("Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            submit_signup = st.form_submit_button("Create Account", use_container_width=True)
            
            if submit_signup:
                if new_email and new_password and confirm_password:
                    if new_password == confirm_password:
                        res = sign_up(new_email, new_password)
                        if res["success"]:
                            st.success("Account created! Please login.")
                        else:
                            st.error(f"Signup failed: {res['error']}")
                    else:
                        st.error("Passwords do not match.")
                else:
                    st.warning("Please fill in all fields.")
