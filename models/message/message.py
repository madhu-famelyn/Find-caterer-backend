import uuid
from sqlalchemy import Column, String, TIMESTAMP, ForeignKey, text, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID

from config.db.session import Base


class Message(Base):
    __tablename__ = "messages"

    # -------------------------------------------------
    # Primary Key
    # -------------------------------------------------
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)

    # -------------------------------------------------
    # Relations
    # -------------------------------------------------
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    caterer_id = Column(
        UUID(as_uuid=True),
        ForeignKey("caterers.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # -------------------------------------------------
    # Snapshot User Info (VERY SMART DESIGN)
    # -------------------------------------------------
    email = Column(String, nullable=False)
    user_full_name = Column(String, nullable=False)
    user_phone_number = Column(String, nullable=False)

    # -------------------------------------------------
    # Message Content
    # -------------------------------------------------
    message = Column(String, nullable=False)

    # Who sent it? ("user" / "caterer")
    sender_type = Column(String(20), nullable=False, default="user")

    # Read status
    is_read = Column(Boolean, default=False)

    # -------------------------------------------------
    # Timestamps
    # -------------------------------------------------
    created_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
        index=True
    )

    updated_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now()
    )

    # -------------------------------------------------
    # Relationships
    # -------------------------------------------------
    user = relationship("User", back_populates="messages")
    caterer = relationship("Caterer", back_populates="messages")
