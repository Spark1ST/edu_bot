from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict

class UserBase(BaseModel):
    email: EmailStr
    username: str
    is_admin: bool = False

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    uid: str
    enrolled_courses: List[str] = []
    progress: Dict = {}

class CourseBase(BaseModel):
    title: str
    description: str
    instructor: str
    image_url: Optional[str] = None

class CourseCreate(CourseBase):
    pass

class CourseResponse(CourseBase):
    id: str
    modules: List[Dict] = []

class ChatMessage(BaseModel):
    sender: str  # "user" or "assistant"
    content: str
    timestamp: Optional[str] = None