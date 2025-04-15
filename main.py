# main.py
from pydantic import BaseModel
from model import get_response
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from firebase_admin import auth
from fastpi import crud
from fastpi import models
# from fastpi.firebase import firebase
from typing import List
import uvicorn

app = FastAPI()

# Enable CORS for Streamlit
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (use specific domain in production)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        decoded_token = auth.verify_id_token(credentials.credentials)
        return decoded_token['uid']
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )

# User Routes
@app.post("/users/", response_model=models.UserResponse)
def create_user(user: models.UserCreate):
    try:
        uid = crud.create_user(user.dict())
        return crud.get_user(uid)
    except auth.EmailAlreadyExistsError:
        raise HTTPException(status_code=400, detail="Email already exists")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/users/me", response_model=models.UserResponse)
def read_current_user(uid: str = Depends(get_current_user)):
    user = crud.get_user(uid)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.get("/users/", response_model=List[models.UserResponse])
def read_all_users():
    return crud.get_all_users()

@app.delete("/users/{uid}")
def delete_user(uid: str, current_user: str = Depends(get_current_user)):
    if uid != current_user:
        raise HTTPException(status_code=403, detail="Cannot delete other users")
    try:
        crud.delete_user(uid)
        return {"message": "User deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Course Routes
@app.post("/courses/", response_model=models.CourseResponse)
def create_course(course: models.CourseCreate, uid: str = Depends(get_current_user)):
    try:
        course_id = crud.create_course(course.dict())
        return crud.get_course(course_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/courses/", response_model=List[models.CourseResponse])
def read_all_courses():
    return crud.get_all_courses()

@app.get("/courses/{course_id}", response_model=models.CourseResponse)
def read_course(course_id: str):
    course = crud.get_course(course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course

@app.put("/courses/{course_id}", response_model=models.CourseResponse)
def update_course(course_id: str, updates: dict, uid: str = Depends(get_current_user)):
    try:
        crud.update_course(course_id, updates)
        return crud.get_course(course_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/courses/{course_id}")
def delete_course(course_id: str, uid: str = Depends(get_current_user)):
    try:
        crud.delete_course(course_id)
        return {"message": "Course deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/courses/{course_id}/enroll")
def enroll_in_course(course_id: str, uid: str = Depends(get_current_user)):
    try:
        crud.enroll_user_in_course(uid, course_id)
        return {"message": "Enrolled successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Chat Routes
@app.post("/chat/", response_model=dict)
def post_message(message: models.ChatMessage, uid: str = Depends(get_current_user)):
    try:
        message_id = crud.add_chat_message(uid, message.dict())
        return {"id": message_id, **message.dict()}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/chat/", response_model=List[models.ChatMessage])
def get_chat_history(uid: str = Depends(get_current_user)):
    return crud.get_chat_history(uid)
class PromptRequest(BaseModel):
    prompt: str
    username: str

@app.post("/generate")
def generate_response(data: PromptRequest):
    result = get_response(data.prompt)
    return {"response": result}
