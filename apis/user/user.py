from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from config.db.session import get_db
from schema.user.user import UserCreate, UserUpdate, UserRead
from service.user.user import (
    create_user,
    get_user_by_id,
    update_user,
    list_users,
)

# Router (NO prefix here)
router = APIRouter()


# --------------------------------
# CREATE USER
# POST /api/v1/user
# --------------------------------
@router.post(
    "",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED
)
def create_user_api(
    payload: UserCreate,
    db: Session = Depends(get_db)
):
    return create_user(db, payload)


# --------------------------------
# GET USER BY ID
# GET /api/v1/user/{user_id}
# --------------------------------
@router.get(
    "/{user_id}",
    response_model=UserRead
)
def get_user_api(
    user_id: UUID,
    db: Session = Depends(get_db)
):
    return get_user_by_id(db, user_id)


# --------------------------------
# UPDATE USER
# PUT /api/v1/user/{user_id}
# --------------------------------
@router.put(
    "/{user_id}",
    response_model=UserRead
)
def update_user_api(
    user_id: UUID,
    payload: UserUpdate,
    db: Session = Depends(get_db)
):
    return update_user(db, user_id, payload)


@router.get(
    "",
    response_model=List[UserRead]
)
def list_users_api(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    return list_users(db, skip, limit)
