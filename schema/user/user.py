# schemas/user.py
from typing import Optional
from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, constr


# ---------------------------
# BASE SCHEMA (shared fields)
# ---------------------------
class UserBase(BaseModel):
    user_name: str = Field(..., max_length=255)
    phone_number: str = Field(..., max_length=20)
    email: Optional[EmailStr] = None


# ---------------------------
# CREATE USER SCHEMA
# ---------------------------
class UserCreate(UserBase):
    password: constr(min_length=8)  # plain password input, will be hashed


# ---------------------------
# UPDATE USER SCHEMA (optional fields)
# ---------------------------
class UserUpdate(BaseModel):
    user_name: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[constr(min_length=8)] = None  # optional password update


# ---------------------------
# READ USER SCHEMA
# ---------------------------
class UserRead(UserBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # allows reading from SQLAlchemy models




