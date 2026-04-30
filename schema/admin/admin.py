from pydantic import BaseModel, EmailStr, Field
from uuid import UUID
from datetime import datetime
from typing import Optional


# -------------------------
# Base Schema
# -------------------------
class AdminBase(BaseModel):
    admin_name: str = Field(..., max_length=255)
    email: Optional[EmailStr] = None


# -------------------------
# Create Schema
# role NOT required (DB default = admin)
# -------------------------
class AdminCreate(AdminBase):
    password: str = Field(..., min_length=8)


# -------------------------
# Response Schema
# role INCLUDED
# -------------------------
class AdminResponse(AdminBase):
    id: UUID
    role: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
