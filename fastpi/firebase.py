import os
import json
import tempfile
import firebase_admin
from firebase_admin import credentials, auth, firestore
import streamlit as st

def initialize_firebase():
    if not firebase_admin._apps:  # Check if Firebase has already been initialized
        firebase_key_str = os.environ.get("FIREBASE_ADMIN_KEY")

        if not firebase_key_str:
            st.error("Firebase Admin Key is missing.")
            st.stop()

        # Parse the JSON string to a dictionary
        try:
            firebase_key_dict = json.loads(firebase_key_str)
        except json.JSONDecodeError as e:
            st.error(f"Failed to parse Firebase key. Check its format: {e}")
            st.stop()

        try:
            # Initialize Firebase Admin SDK using the dictionary directly
            cred = credentials.Certificate(firebase_key_dict)
            firebase_admin.initialize_app(cred)
        except Exception as e:
            st.error(f"Failed to initialize Firebase: {e}")
            st.stop()

    return {
        'auth': auth,
        'db': firestore.client()
    }

# Make sure to call this function to initialize Firebase before using Firestore
firebase = initialize_firebase()
