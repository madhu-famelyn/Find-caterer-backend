from typing import List
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from passlib.context import CryptContext     

from models.user.user import User
from schema.user.user import UserCreate, UserUpdate

# --------------------------------
# Password Hasher
# --------------------------------
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)


# --------------------------------
# CREATE USER
# --------------------------------
def create_user(db: Session, payload: UserCreate) -> User:
    try:
        user = User(
            user_name=payload.user_name,
            phone_number=payload.phone_number,
            email=payload.email,
            password_hash=hash_password(payload.password),
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Phone number or email already exists"
        )


# --------------------------------
# GET USER BY ID
# --------------------------------
def get_user_by_id(db: Session, user_id: UUID) -> User:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user


# --------------------------------
# UPDATE USER
# --------------------------------
def update_user(db: Session, user_id: UUID, payload: UserUpdate) -> User:
    user = get_user_by_id(db, user_id)

    update_data = payload.model_dump(exclude_unset=True)

    if "password" in update_data:
        # Hash password if provided
        update_data["password_hash"] = hash_password(update_data.pop("password"))

    for field, value in update_data.items():
        setattr(user, field, value)

    db.commit()
    db.refresh(user)
    return user


# --------------------------------
# LIST USERS
# --------------------------------
def list_users(db: Session, skip: int = 0, limit: int = 20) -> List[User]:
    return db.query(User).offset(skip).limit(limit).all()
