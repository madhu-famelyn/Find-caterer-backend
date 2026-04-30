from pydantic import BaseModel, EmailStr, Field
from uuid import UUID
from datetime import datetime


class MessageCreate(BaseModel):
    user_id: UUID = Field(
        ...,
        description="ID of the user sending the message"
    )

    caterer_id: UUID = Field(
        ...,
        description="ID of the caterer receiving the message"
    )

    email: EmailStr = Field(
        ...,
        description="Email of the user"
    )

    user_full_name: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Full name of the user"
    )

    user_phone_number: str = Field(
        ...,
        min_length=10,
        max_length=15,
        description="Phone number of the user"
    )

    message: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="The message content"
    )




class MessageResponse(BaseModel):
    id: UUID
    user_id: UUID
    caterer_id: UUID

    email: EmailStr
    user_full_name: str
    user_phone_number: str
    message: str

    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True   # ✅ Pydantic v2 (Replaces orm_mode)
