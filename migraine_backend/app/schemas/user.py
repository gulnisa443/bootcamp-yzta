from pydantic import BaseModel, EmailStr
from typing import Optional

class UserCreate(BaseModel):
    name: Optional[str] = None
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserEmailUpdate(BaseModel):
    email: EmailStr

class UserPasswordUpdate(BaseModel):
    password: str

class UserProfileResponse(BaseModel):
    id: int
    name: Optional[str] = None
    email: EmailStr
    created_at: str
    total_entries: int
    last_login: Optional[str] = None

    class Config:
        orm_mode = True
