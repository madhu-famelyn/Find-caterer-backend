import uuid
from enum import Enum as PyEnum

from sqlalchemy import (
    Column,
    String,
    Integer, 
    Text,
    Boolean,
    DateTime,
    Enum,
    Float
)

from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from config.db.session import Base


class CatererStatus(PyEnum):
    pending = "pending"
    accepted = "accepted"
    rejected = "rejected"


class Caterer(Base):
    __tablename__ = "caterers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
 
    business_name = Column(String(255), nullable=True)
    phone_number = Column(String(20), unique=True, nullable=True)
    email = Column(String(255), unique=True, nullable=True)
    password_hash = Column(String(255), nullable=True)

    # About
    description = Column(Text, nullable=True)

    # Preferences
    cuisine_type = Column(String(100), nullable=True)
    event_type = Column(String(100), nullable=True)
    price_range = Column(String(50), nullable=True)

    # Capacity
    capacity_min = Column(Integer, nullable=True)
    capacity_max = Column(Integer, nullable=True)

    # Existing Address Fields
    country = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    city = Column(String(100), nullable=True)
    pincode = Column(String(20), nullable=True)
    address_line = Column(Text, nullable=True)

    # Status
    status = Column(
        Enum(CatererStatus, name="caterer_status_enum"),
        nullable=False,
        default=CatererStatus.pending
    )

    # ---------------------------
    # 🔥 NEWLY ADDED COLUMNS (FROM EXCEL MODEL)
    # ---------------------------
    main_image = Column(String, nullable=True)
     # Mandatory Excel Fields
    website = Column(String(255), nullable=True)

    # Location
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)

    # Ratings
    rating_count = Column(Integer, nullable=True)
    rating = Column(Float, nullable=True)

    # Photos from Excel (Google URLs / folder images)
    photo_folder_name = Column(JSONB, nullable=True)
    # Example:
    # [
    #   "https://lh5.googleusercontent.com/p/AF1Qip...",
    #   "https://lh5.googleusercontent.com/p/AF1Qip..."
    # ]

    # ---------------------------
    # Meta
    # ---------------------------
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    messages = relationship(
    "Message",
    back_populates="caterer",
    cascade="all, delete-orphan"
)
