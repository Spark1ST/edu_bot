import streamlit as st
from firebase_admin import credentials, firestore, auth  # Add this import
from utils.session import (
    initialize_session_state,
    verify_password,
    load_user_data,
    save_user_data,
    db  # Import db from session
)

def show_authentication():
    initialize_session_state()
    st.title("Welcome to QuestCourse Forge")
    
    tab1, tab2 = st.tabs(["Sign In", "Sign Up"])
    
    # Sign In Tab (unchanged)
    with tab1:
        st.header("Sign In")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        
        if st.button("Login", type="primary"):
            if not email or not password:
                st.error("Please enter both email and password")
            else:
                is_valid, result = verify_password(email, password)
                if is_valid:
                    try:
                        user = auth.get_user_by_email(email)
                        user_data = load_user_data(user.uid) or {
                            "email": email,
                            "username": email.split('@')[0],
                            "enrolled_courses": [],
                            "progress": {}
                        }
                        
                        st.session_state.update({
                            "logged_in": True,
                            "uid": user.uid,
                            "email": email,
                            "username": user_data.get("username"),
                            "user_data": user_data,
                            "is_admin": user_data.get("is_admin", False), 
                            "page": "dashboard"
                        })
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
                else:
                    st.error(f"Login failed: {result}")

    # Sign Up Tab - Fixed Version
    with tab2:
        st.header("Create Account")
        email = st.text_input("Email", key="signup_email")
        password = st.text_input("Password", type="password", key="signup_password")
        username = st.text_input("Username")
        
        if st.button("Sign Up", type="primary"):
            if not all([email, password, username]):
                st.error("Please fill all fields")
            else:
                try:
                    # Create Firebase auth user
                    user = auth.create_user(
                        email=email,
                        password=password,
                        display_name=username
                    )
                    
                    # Create user document in Firestore
                    user_data = {
                        "username": username,
                        "email": email,
                        "is_admin": False,
                        "enrolled_courses": [],
                        "progress": {},
                        "created_at": firestore.SERVER_TIMESTAMP
                    }
                    
                    # Save to Firestore
                    db.collection("users").document(user.uid).set(user_data)
                    
                    # Update session
                    st.session_state.update({
                        "logged_in": True,
                        "uid": user.uid,
                        "email": email,
                        "username": username,
                        "user_data": user_data,
                        "page": "dashboard"
                    })
                    st.success("Account created successfully!")
                    st.rerun()
                    
                except auth.EmailAlreadyExistsError:
                    st.error("Email already exists. Please sign in instead.")
                except Exception as e:
                    st.error(f"Sign up failed: {str(e)}")