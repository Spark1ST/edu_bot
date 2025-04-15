import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore, auth
from firebase_admin.exceptions import FirebaseError
import requests
from datetime import datetime
from pathlib import Path
import json
import os
import tempfile

## Get the Firebase Admin key from environment variables
firebase_key_str = os.environ["FIREBASE_ADMIN_KEY"]

# Parse the JSON string to a dictionary
try:
    firebase_key_dict = json.loads(firebase_key_str)
except json.JSONDecodeError as e:
    print(f"Failed to parse Firebase key. Check its format: {e}")
    exit(1)

# Save the JSON to a temporary file
with tempfile.NamedTemporaryFile(delete=False, mode='w') as temp_file:
    json.dump(firebase_key_dict, temp_file)
    temp_file_path = temp_file.name

# Initialize Firebase Admin SDK using the temporary file
try:
    cred = credentials.Certificate(temp_file_path)
    firebase_admin.initialize_app(cred)
    print("Firebase initialized successfully")
except Exception as e:
    print(f"Failed to initialize Firebase: {e}")
    exit(1)

# Optionally, clean up the temporary file if not needed anymore
os.remove(temp_file_path)

db = firestore.client()

def initialize_session_state():
    defaults = {
        "logged_in": False,
        "uid": None,
        "email": None,
        "username": None,
        "is_admin": False,
        "page": "auth",
        "selected_course": None,
        "current_module": None,
        "user_data": {}
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)
def check_session_state():
    """Ensure session state is properly initialized"""
    initialize_session_state()
def verify_password(email, password):
    API_KEY = st.secrets["FIREBASE_API_KEY"]
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={API_KEY}"
    try:
        response = requests.post(url, json={
            "email": email,
            "password": password,
            "returnSecureToken": True
        })
        if response.status_code == 200:
            return True, response.json()
        return False, response.json().get('error', {}).get('message', 'Login failed')
    except Exception as e:
        return False, str(e)

def load_user_data(uid):
    try:
        doc = db.collection("users").document(uid).get()
        return doc.to_dict() or {}
    except Exception as e:
        st.error(f"Error loading user: {str(e)}")
        return {}

def save_user_data(uid, data):
    try:
        db.collection("users").document(uid).set(data, merge=True)
        return True
    except Exception as e:
        st.error(f"Error saving user: {str(e)}")
        return False

def load_course_data(course_id=None):
    """Load course data from local JSON files"""
    if course_id:
        course_file = Path(f"data/courses/{course_id}.json")
        if course_file.exists():
            with open(course_file, "r") as f:
                return json.load(f)
        return None
    else:
        courses = []
        for course_file in Path("data/courses").glob("*.json"):
            with open(course_file, "r") as f:
                courses.append(json.load(f))
        return courses


def update_user_progress(uid, course_id, module_id, progress_data):
    try:
        db.collection("users").document(uid).update({
            f"progress.{course_id}.{module_id}": progress_data,
            "last_updated": datetime.now()
        })
        return True
    except Exception as e:
        st.error(f"Error updating progress: {str(e)}")
        return False
