import pyrebase
import streamlit as st

# Firebase configuration
firebase_config = {
    "apiKey": "AIzaSyBFrhkyt9gg1E393DbaKIO9gO9jW04kiWQ",
    "authDomain": "growth-engine-e9418.firebaseapp.com",
    "projectId": "growth-engine-e9418",
    "storageBucket": "growth-engine-e9418.firebasestorage.app",
    "messagingSenderId": "741659135978",
    "appId": "1:741659135978:web:6a8afb9dad95c4c9c16c93",
}

# Initialize Firebase
firebase = pyrebase.initialize_app(firebase_config)
auth = firebase.auth()

def sign_up(email, password):
    """Creates a new user in Firebase Auth."""
    try:
        user = auth.create_user_with_email_and_password(email, password)
        return {"success": True, "user": user}
    except Exception as e:
        return {"success": False, "error": str(e)}

def sign_in(email, password):
    """Authenticates a user with Firebase Auth."""
    try:
        user = auth.sign_in_with_email_and_password(email, password)
        return {"success": True, "user": user}
    except Exception as e:
        return {"success": False, "error": str(e)}

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
