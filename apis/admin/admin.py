from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from config.db.session import get_db
from schema.admin.admin import AdminCreate, AdminResponse
from service.admin.admin import AdminService


router = APIRouter(
    prefix="/admin",
    tags=["Admin"]
)
  
   
# -------------------------
# Create Admin        
# -------------------------
@router.post(
    "/create",
    response_model=AdminResponse,
    status_code=status.HTTP_201_CREATED
)
def create_admin(
    data: AdminCreate,
    db: Session = Depends(get_db)
):
    admin = AdminService.create_admin(db=db, data=data)
    return admin


# -------------------------
# Admin Login
# -------------------------
@router.post(
    "/login",
    response_model=AdminResponse,
    status_code=status.HTTP_200_OK
)
def admin_login(
    email: str,
    password: str,
    db: Session = Depends(get_db)
):
    admin = AdminService.authenticate_admin(
        db=db,
        email=email,
        password=password
    )
    return admin
