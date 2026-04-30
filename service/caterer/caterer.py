from typing import List, Optional
from uuid import UUID
from sqlalchemy import func, or_
from sqlalchemy.orm import Session
import math
from sqlalchemy.exc import IntegrityError
from fastapi import UploadFile, status, HTTPException
import ast
import pandas as pd
from models.caterer.caterer import Caterer, CatererStatus
from utils.security import hash_password
from schema.caterer.caterer import (
    CatererCreate,
    CatererUpdate,
    CatererStatusUpdate
)
import uuid
import requests
import ast
from passlib.context import CryptContext
from dotenv import load_dotenv
import os
import boto3

# --------------------------------
# Password Hasher
# --------------------------------
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# -------------------------------------------------
# LOAD ENV
# -------------------------------------------------
load_dotenv()

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION")
AWS_BUCKET_NAME = os.getenv("AWS_BUCKET_NAME")

# -------------------------------------------------
# S3 CLIENT
# -------------------------------------------------
s3_client = boto3.client(
    "s3",
    region_name=AWS_REGION,
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
)



def normalize_google_image_url(url: str) -> str:
    """
    Converts Google preview URLs into downloadable format.
    Forces size parameter required by Google.
    """
    if not url:
        return ""

    # Remove existing parameters like =w900-h900
    base = url.split("=")[0]

    # Force supported size
    return f"{base}=s800"

# -------------------------------------------------
# HELPERS
# -------------------------------------------------
def parse_image_list(value):
    """
    Converts Excel cell value to Python list safely
    """
    if not value or str(value).lower() == "nan":
        return []

    if isinstance(value, list):
        return value

    if isinstance(value, str):
        try:
            return ast.literal_eval(value)
        except Exception:
            return []
    return []


def upload_file_to_s3(file: UploadFile, caterer_id: UUID) -> str:

    file_extension = file.filename.split(".")[-1]
    file_key = f"caterers/{caterer_id}/main.{file_extension}"

    s3_client.upload_fileobj(
        file.file,
        AWS_BUCKET_NAME,
        file_key,
        ExtraArgs={
            "ContentType": file.content_type
        }
    )

    return f"https://{AWS_BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{file_key}"


def upload_image_to_s3(image_url: str) -> str:
    """
    Download image from URL and upload to S3
    Returns S3 public URL
    """
    response = requests.get(image_url, timeout=10)
    response.raise_for_status()

    file_name = f"caterers/{uuid.uuid4()}.jpg"

    s3_client.put_object(
        Bucket=AWS_BUCKET_NAME,
        Key=file_name,
        Body=response.content,
        ContentType="image/jpeg",
    )

    return f"https://{AWS_BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{file_name}"



import requests
import uuid
from urllib.parse import urlparse
import mimetypes


def upload_image_to_s3_create_caterer(file: UploadFile) -> str:
    """
    Uploads FastAPI UploadFile directly to S3.
    Returns public S3 URL.
    """

    ext = file.filename.split(".")[-1].lower()
    if ext not in ["jpg", "jpeg", "png", "webp"]:
        ext = "jpg"

    file_name = f"caterers/{uuid.uuid4()}.{ext}"

    content_type = file.content_type or "image/jpeg"

    s3_client.put_object(
        Bucket=AWS_BUCKET_NAME,
        Key=file_name,
        Body=file.file,   # ✅ IMPORTANT
        ContentType=content_type,
    )

    return f"https://{AWS_BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{file_name}"

def create_caterer(db: Session, payload: CatererCreate) -> Caterer:
    try:

        caterer = Caterer(
            business_name=payload.business_name,
            phone_number=payload.phone_number,
            email=payload.email,
            password_hash=hash_password(payload.password) if payload.password else None,

            description=payload.description,

            cuisine_type=payload.cuisine_type,
            event_type=payload.event_type,
            price_range=payload.price_range,

            capacity_min=payload.capacity_min,
            capacity_max=payload.capacity_max,

            country=payload.country,
            state=payload.state,
            city=payload.city,
            pincode=payload.pincode,
            address_line=payload.address_line,

            website=payload.website,

            latitude=payload.latitude,
            longitude=payload.longitude,

            rating_count=payload.rating_count,
            rating=payload.rating,

            # ✅ STORE MAIN IMAGE
            main_image=payload.main_image,

            # ✅ STORE GALLERY
            photo_folder_name=payload.photo_folder_name or [],

            status=CatererStatus.pending,
            is_active=True
        )

        db.add(caterer)
        db.commit()
        db.refresh(caterer)

        return caterer

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Phone number or email already exists"
        )





def upload_or_update_caterer_main_image(
    db: Session,
    caterer_id: UUID,
    file: UploadFile
):
    caterer = db.query(Caterer).filter(Caterer.id == caterer_id).first()

    if not caterer:
        raise HTTPException(status_code=404, detail="Caterer not found")

    # Upload to S3
    image_url = upload_file_to_s3(file, caterer_id)

    # UPSERT
    caterer.main_image = image_url

    db.commit()
    db.refresh(caterer)

    return caterer



def sanitize_value(value):
    """
    Convert unsafe values into JSON-safe ones.
    """

    # Fix NaN / Infinity
    if isinstance(value, float):
        if math.isnan(value) or math.isinf(value):
            return 0.0

    # Fix stringified list
    if isinstance(value, str):
        try:
            parsed = ast.literal_eval(value)
            if isinstance(parsed, list):
                return parsed
        except Exception:
            pass

    return value
# --------------------------------
# GET CATERER BY ID
# --------------------------------
def get_caterer_by_id(db: Session, caterer_id: UUID) -> Caterer:
    caterer = db.query(Caterer).filter(
        Caterer.id == caterer_id
    ).first()

    if not caterer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Caterer not found"
        )

    # ✅ SANITIZE ALL COLUMNS AUTOMATICALLY
    for column in caterer.__table__.columns:
        value = getattr(caterer, column.name)
        cleaned_value = sanitize_value(value)
        setattr(caterer, column.name, cleaned_value)

    return caterer


# --------------------------------
# UPDATE CATERER (PROFILE)
# --------------------------------
def update_caterer(
    db: Session,
    caterer_id: UUID,
    payload: CatererUpdate
) -> Caterer:

    caterer = get_caterer_by_id(db, caterer_id)

    update_data = payload.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(caterer, field, value)

    db.commit()
    db.refresh(caterer)

    return caterer


# --------------------------------
# UPDATE CATERER STATUS (ADMIN)
# --------------------------------

import math

def sanitize_for_json(obj):
    """
    Recursively sanitize an object so it never breaks JSON serialization.
    Converts:
        NaN -> None
        Infinity -> None
        -Infinity -> None
    Leaves None as-is (valid JSON).
    """

    # Handle floats
    if isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            return None
        return obj

    # Handle dict
    if isinstance(obj, dict):
        return {k: sanitize_for_json(v) for k, v in obj.items()}

    # Handle list / tuple / set
    if isinstance(obj, (list, tuple, set)):
        return [sanitize_for_json(v) for v in obj]

    # Handle SQLAlchemy model
    if hasattr(obj, "__table__"):
        for column in obj.__table__.columns:
            value = getattr(obj, column.name)
            setattr(obj, column.name, sanitize_for_json(value))
        return obj

    return obj



def get_caterer_by_id(db: Session, caterer_id: UUID) -> Caterer:

    caterer = db.query(Caterer).filter(
        Caterer.id == caterer_id
    ).first()

    if not caterer:
        raise HTTPException(
            status_code=404,
            detail="Caterer not found"
        )

    # ✅ Fix gallery if stored as string
    if isinstance(caterer.photo_folder_name, str):
        try:
            caterer.photo_folder_name = ast.literal_eval(
                caterer.photo_folder_name
            )
        except:
            caterer.photo_folder_name = []

    # ⭐⭐⭐ MOST IMPORTANT LINE
    return sanitize_for_json(caterer)


# --------------------------------
# LIST CATERERS
# --------------------------------
def list_caterers(
    db: Session,
    status: Optional[CatererStatus] = None,
    skip: int = 0,
    limit: int = 20
) -> List[Caterer]:

    query = db.query(Caterer)

    if status:
        query = query.filter(Caterer.status == status)

    caterers = query.offset(skip).limit(limit).all()

    # sanitize NaN values before returning
    for c in caterers:
        sanitize_for_json(c)

    return caterers



import math
from fastapi.encoders import jsonable_encoder


def sanitize_model(model):
    for column in model.__table__.columns:
        value = getattr(model, column.name)

        # Replace NaN / Infinity
        if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
            setattr(model, column.name, None)

    return model


def update_caterer_status(
    db: Session,
    caterer_id: UUID,
    new_status: CatererStatus
):

    caterer = db.query(Caterer).filter(
        Caterer.id == caterer_id
    ).first()

    if not caterer:
        raise HTTPException(
            status_code=404,
            detail="Caterer not found"
        )

    if caterer.status == new_status:
        raise HTTPException(
            status_code=400,
            detail=f"Caterer already {new_status}"
        )

    try:
        caterer.status = new_status

        db.commit()
        db.refresh(caterer)

        # ⭐⭐⭐ CRITICAL LINE
        sanitize_model(caterer)

        # ⭐ EVEN SAFER
        return jsonable_encoder(caterer)

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )



def bulk_upload_caterers(
    db: Session,
    file: UploadFile,
    country: str,
    state: str | None = None,
    city: str | None = None
):

    if not country or not country.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Country is required"
        )

    state = state.strip() if state and state.strip() else None
    city = city.strip() if city and city.strip() else None

    if not file.filename.endswith((".xlsx", ".xls")):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only Excel files are allowed"
        )

    try:
        df = pd.read_excel(file.file, engine="openpyxl")
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to read Excel file: {str(e)}"
        )

    df.columns = (
        df.columns.astype(str)
        .str.strip()
        .str.replace("\u00a0", " ", regex=False)
    )

    required_columns = [
        "Name",
        "Address",
        "Phone Number",
        "Website",
        "Latitude",
        "Longitude",
        "Rating Count",
        "Rating",
        "Photo folder name"
    ]

    missing = [c for c in required_columns if c not in df.columns]
    if missing:
        raise HTTPException(
            status_code=400,
            detail=f"Missing required columns: {missing}"
        )

    caterers_to_insert = []
    failed_rows = []

    for index, row in df.iterrows():
        row_number = index + 2

        try:
            name = str(row["Name"]).strip()
            phone = str(row["Phone Number"]).strip()

            if not name:
                raise ValueError("Name is required")

            if not phone or phone.lower() == "nan":
                raise ValueError("Phone Number is required")

            latitude = float(row["Latitude"]) if not pd.isna(row["Latitude"]) else None
            longitude = float(row["Longitude"]) if not pd.isna(row["Longitude"]) else None

            rating_count = None
            if not pd.isna(row["Rating Count"]):
                rating_count = int(float(str(row["Rating Count"]).replace(",", "")))

            rating = None
            if not pd.isna(row["Rating"]):
                rating = float(row["Rating"])
                if not (0 <= rating <= 5):
                    raise ValueError("Rating must be between 0 and 5")

            # 🔥 IMAGE PROCESSING
            raw_images = parse_image_list(row["Photo folder name"])
            s3_images = []

            for img_url in raw_images:
                normalized_url = normalize_google_image_url(img_url)

                try:
                    s3_url = upload_image_to_s3(normalized_url)
                    s3_images.append(s3_url if s3_url else normalized_url)

                except Exception as e:
                    print(f"Image upload failed: {normalized_url} | {e}")
                    s3_images.append(normalized_url)

            caterer = Caterer(
                business_name=name,
                address=str(row["Address"]).strip(),
                phone_number=phone,
                website=row["Website"],

                latitude=latitude,
                longitude=longitude,

                rating_count=rating_count,
                rating=rating,

                photo_folder_name=s3_images or [],

                country=country,
                state=state,
                city=city,

                # ✅ AUTO APPROVED
                status=CatererStatus.accepted,

                is_active=True
            )

            caterers_to_insert.append(caterer)

        except Exception as e:
            failed_rows.append(f"Row {row_number}: {str(e)}")

    # ⭐ SINGLE COMMIT (VERY FAST)
    try:
        db.add_all(caterers_to_insert)
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="Bulk insert failed due to duplicate data."
        )

    return {
        "total_rows": len(df),
        "success_count": len(caterers_to_insert),
        "failed_count": len(failed_rows),
        "failed_rows": failed_rows
    }




def get_caterers_by_location(
    db: Session,
    location: str,
    page: int = 1,
    limit: int = 10,
    event_types: Optional[List[str]] = None,
    cuisines: Optional[List[str]] = None,
    min_rating: Optional[float] = None,
) -> List[Caterer]:

    # -------------------------------
    # VALIDATION
    # -------------------------------
    if not location or not location.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Location is required"
        )

    if page < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Page must be >= 1"
        )

    # Pagination cap
    limit = min(max(limit, 1), 10)
    offset = (page - 1) * limit
    location = location.strip().lower()

    # -------------------------------
    # BASE QUERY (ONLY ACCEPTED)
    # -------------------------------
    query = db.query(Caterer).filter(
        Caterer.is_active.is_(True),

        # ⭐ CRITICAL FILTER
        Caterer.status == CatererStatus.accepted,

        or_(
            func.lower(Caterer.country).like(f"%{location}%"),
            func.lower(Caterer.state).like(f"%{location}%"),
            func.lower(Caterer.city).like(f"%{location}%"),
        )
    )

    # -------------------------------
    # EVENT TYPE FILTER
    # -------------------------------
    if event_types:
        event_types = [e.strip().lower() for e in event_types]

        query = query.filter(
            Caterer.event_type.isnot(None),
            func.lower(Caterer.event_type).in_(event_types)
        )

    # -------------------------------
    # CUISINE FILTER
    # -------------------------------
    if cuisines:
        cuisines = [c.strip().lower() for c in cuisines]

        query = query.filter(
            Caterer.cuisine_type.isnot(None),
            func.lower(Caterer.cuisine_type).in_(cuisines)
        )

    # -------------------------------
    # RATING FILTER
    # -------------------------------
    if min_rating is not None:
        query = query.filter(
            Caterer.rating.isnot(None),
            Caterer.rating >= min_rating
        )

    # -------------------------------
    # SMART MARKETPLACE ORDERING
    # -------------------------------
    query = query.order_by(
        Caterer.rating.desc().nullslast(),
        Caterer.rating_count.desc().nullslast(),
        Caterer.created_at.desc()
    )

    # -------------------------------
    # PAGINATION
    # -------------------------------
    caterers = query.offset(offset).limit(limit).all()

    return caterers