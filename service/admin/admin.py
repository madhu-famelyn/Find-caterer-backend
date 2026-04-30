from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from models.admin.admin import Admin
from schema.admin.admin import AdminCreate
from utils.security import hash_password, verify_password


class AdminService:
    @staticmethod
    def create_admin(db: Session, data: AdminCreate) -> Admin:
        # Check if email already exists
        if data.email:
            existing_admin = (
                db.query(Admin)
                .filter(Admin.email == data.email)
                .first()
            )
            if existing_admin:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Admin with this email already exists"
                )

        # Create admin (role defaults to 'admin')
        admin = Admin(
            admin_name=data.admin_name,
            email=data.email,
            password_hash=hash_password(data.password)
        )

        db.add(admin)
        db.commit()
        db.refresh(admin)
        return admin

    @staticmethod
    def get_admin_by_email(db: Session, email: str) -> Admin | None:
        return db.query(Admin).filter(Admin.email == email).first()

    @staticmethod
    def authenticate_admin(
        db: Session,
        email: str,
        password: str
    ) -> Admin:
        admin = AdminService.get_admin_by_email(db, email)

        if not admin or not verify_password(password, admin.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )

        return admin
