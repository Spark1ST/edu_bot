from datetime import datetime
from firebase_admin import auth, firestore
from fastpi.models import UserResponse, CourseResponse
from firebase_admin import credentials, firestore, auth
from fastpi.firebase import firebase

db = firebase['db']
auth_client = firebase['auth']

# User Operations
def create_user(user: dict):
    try:
        # Create Firebase auth user
        auth_user = auth_client.create_user(
            email=user['email'],
            password=user['password'],
            display_name=user['username']
        )
        
        # Create Firestore document
        user_data = {
            'username': user['username'],
            'email': user['email'],
            'is_admin': user.get('is_admin', False),
            'enrolled_courses': [],
            'progress': {},
            'created_at': datetime.now()
        }
        
        db.collection('users').document(auth_user.uid).set(user_data)
        return auth_user.uid
    except Exception as e:
        raise e

def get_user(uid: str):
    doc = db.collection('users').document(uid).get()
    if doc.exists:
        user_data = doc.to_dict()
        return UserResponse(uid=uid, **user_data)
    return None

def get_all_users():
    users = []
    docs = db.collection('users').stream()
    for doc in docs:
        user_data = doc.to_dict()
        users.append(UserResponse(uid=doc.id, **user_data))
    return users

def delete_user(uid: str):
    try:
        auth_client.delete_user(uid)
        db.collection('users').document(uid).delete()
        return True
    except Exception as e:
        raise e

# Course Operations
def create_course(course: dict):
    try:
        doc_ref = db.collection('courses').document()
        course_data = {
            **course,
            'id': doc_ref.id,
            'modules': [],
            'created_at': datetime.now()
        }
        doc_ref.set(course_data)
        return doc_ref.id
    except Exception as e:
        raise e

def get_course(course_id: str):
    doc = db.collection('courses').document(course_id).get()
    if doc.exists:
        return CourseResponse(**doc.to_dict())
    return None

def get_all_courses():
    courses = []
    docs = db.collection('courses').stream()
    for doc in docs:
        course_data = doc.to_dict()
        courses.append(CourseResponse(**course_data))
    return courses

def update_course(course_id: str, updates: dict):
    db.collection('courses').document(course_id).update(updates)
    return True

def delete_course(course_id: str):
    # Remove course from all enrolled users first
    users = db.collection('users').where('enrolled_courses', 'array_contains', course_id).stream()
    for user in users:
        db.collection('users').document(user.id).update({
            'enrolled_courses': firestore.ArrayRemove([course_id])
        })
    
    # Delete course
    db.collection('courses').document(course_id).delete()
    return True

def enroll_user_in_course(uid: str, course_id: str):
    db.collection('users').document(uid).update({
        'enrolled_courses': firestore.ArrayUnion([course_id])
    })
    return True

# Chat Operations
def add_chat_message(uid: str, message: dict):
    chat_ref = db.collection('users').document(uid).collection('chat').document()
    message['timestamp'] = datetime.now()
    chat_ref.set(message)
    return chat_ref.id

def get_chat_history(uid: str, limit: int = 20):
    messages = []
    docs = db.collection('users').document(uid).collection('chat').order_by('timestamp', direction='DESCENDING').limit(limit).stream()
    for doc in docs:
        messages.append(doc.to_dict())
    return messages[::-1]  # Return in chronological order
