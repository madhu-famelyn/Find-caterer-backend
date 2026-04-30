from typing import Optional, List
from uuid import UUID
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, EmailStr, Field, ConfigDict


# --------------------------------
# ENUM (match DB enum exactly)
# --------------------------------
class CatererStatus(str, Enum):
    pending = "pending"
    accepted = "accepted"
    rejected = "rejected"


# --------------------------------
# BASE SCHEMA (shared fields)
# --------------------------------
class CatererBase(BaseModel):
    # Business Info
    business_name: Optional[str] = Field(None, max_length=255)
    phone_number: Optional[str] = Field(None, max_length=20)
    email: Optional[EmailStr] = None

    # About
    description: Optional[str] = None

    # Preferences
    cuisine_type: Optional[str] = None
    event_type: Optional[str] = None
    price_range: Optional[str] = None

    # Capacity
    capacity_min: Optional[int] = None
    capacity_max: Optional[int] = None

    # Existing Address Fields
    country: Optional[str] = None
    state: Optional[str] = None
    city: Optional[str] = None
    pincode: Optional[str] = None
    address_line: Optional[str] = None
    main_image: Optional[str] = None

    # ---------------------------
    # NEW EXCEL-BASED FIELDS
    # ---------------------------

    website: Optional[str] = None

    latitude: Optional[float] = None
    longitude: Optional[float] = None

    rating_count: Optional[int] = None
    rating: Optional[float] = None

    photo_folder_name: Optional[List[str]] = None

    # Meta
    is_active: Optional[bool] = True


# --------------------------------
# CREATE CATERER
# --------------------------------
class CatererCreate(CatererBase):
    password: Optional[str] = Field(None, min_length=6)
    # password → password_hash handled in service layer


# --------------------------------
# UPDATE CATERER (PARTIAL UPDATE)
# --------------------------------
class CatererUpdate(BaseModel):
    business_name: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[EmailStr] = None

    description: Optional[str] = None

    cuisine_type: Optional[str] = None
    event_type: Optional[str] = None
    price_range: Optional[str] = None

    capacity_min: Optional[int] = None
    capacity_max: Optional[int] = None
    

    country: Optional[str] = None
    state: Optional[str] = None
    city: Optional[str] = None
    pincode: Optional[str] = None
    address_line: Optional[str] = None
    website: Optional[str] = None

    latitude: Optional[float] = None
    longitude: Optional[float] = None

    rating_count: Optional[int] = None
    rating: Optional[float] = None

    photo_folder_name: Optional[List[str]] = None

    is_active: Optional[bool] = None


# --------------------------------
# UPDATE STATUS (ADMIN ONLY)
# --------------------------------
class CatererStatusUpdate(BaseModel):
    status: CatererStatus


# --------------------------------
# READ / RESPONSE SCHEMA
# --------------------------------
class CatererRead(BaseModel):
    id: UUID

    business_name: Optional[str]
    phone_number: Optional[str]
    email: Optional[EmailStr]

    description: Optional[str]

    cuisine_type: Optional[str]
    event_type: Optional[str]
    price_range: Optional[str]

    capacity_min: Optional[int]
    capacity_max: Optional[int]

    country: Optional[str]
    state: Optional[str]
    city: Optional[str]
    pincode: Optional[str]
    address_line: Optional[str]
    main_image:Optional[str]

    # Excel-based fields

    website: Optional[str]

    latitude: Optional[float]
    longitude: Optional[float]

    rating_count: Optional[int]
    rating: Optional[float]

    photo_folder_name: Optional[List[str]]

    status: CatererStatus
    is_active: bool

    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True




class CatererBulkUploadResponse(BaseModel):
    total_rows: int
    success_count: int
    failed_count: int
    failed_rows: List[str]


class CatererImageResponse(BaseModel):
    id: UUID
    main_image: str

    class Config:
        from_attributes = True


class CatererListResponse(BaseModel):
    id: UUID
    business_name: str
    phone_number: str
    address: Optional[str] = Field(None, alias="address_line")
    website: Optional[str]

    country: str
    state: Optional[str]
    city: Optional[str]
    cuisine_type: Optional[str] = None

    latitude: Optional[float]
    longitude: Optional[float]
    
    rating_count: Optional[int]
    rating: Optional[float]

    status: str
    main_image:Optional[str]
    is_active: bool
    photo_folder_name: Optional[List[str]]

    class Config:
        from_attributes = True





class CatererStatusPatch(BaseModel):
    id: UUID = Field(..., description="Caterer ID to update")

    status: CatererStatus = Field(
        ...,
        description="Allowed values: pending, accepted, rejected"
    )

    # 🚨 Prevent extra fields
    model_config = ConfigDict(extra="forbid")