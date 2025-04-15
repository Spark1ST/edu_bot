import os
import json
import tempfile
import firebase_admin
from firebase_admin import credentials, auth, firestore

def initialize_firebase():
    if not firebase_admin._apps:  # Check if Firebase has already been initialized
        # Get the Firebase Admin key from environment variables
        firebase_key_str = os.environ["FIREBASE_ADMIN_KEY"]

        # Parse the JSON string to a dictionary
        try:
            firebase_key_dict = json.loads(firebase_key_str)
        except json.JSONDecodeError as e:
            st.error(f"Failed to parse Firebase key. Check its format: {e}")
            st.stop()

        # Save the JSON to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, mode='w') as temp_file:
            json.dump(firebase_key_dict, temp_file)
            temp_file_path = temp_file.name

        # Initialize Firebase Admin SDK using the temporary file
        try:
            cred = credentials.Certificate(temp_file_path)
            firebase_admin.initialize_app(cred)
        except Exception as e:
            st.error(f"Failed to initialize Firebase: {e}")
            st.stop()

        # Optionally, clean up the temporary file
        os.remove(temp_file_path)

    return {
        'auth': auth,
        'db': firestore.client()
    }

# Usage
firebase = initialize_firebase()
