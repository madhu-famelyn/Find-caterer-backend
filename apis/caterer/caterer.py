from typing import List, Optional
from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    UploadFile,
    File,
    Form,
    HTTPException,
    status,
    Query
)
from sqlalchemy.orm import Session

from config.db.session import get_db

from service.caterer.caterer import (
    create_caterer,
    get_caterer_by_id,
    update_caterer,
    list_caterers,
    bulk_upload_caterers,
    get_caterers_by_location,
    upload_or_update_caterer_main_image,
    upload_image_to_s3_create_caterer,
    update_caterer_status
)

from schema.caterer.caterer import (
    CatererCreate,
    CatererUpdate,
    CatererRead,
    CatererBulkUploadResponse,
    CatererListResponse,
    CatererImageResponse,
    CatererStatusPatch
)

from models.caterer.caterer import CatererStatus


router = APIRouter(
    prefix="/caterers",
    tags=["Caterers"]
)

# =========================================================
# CREATE CATERER
# =========================================================








@router.patch(
    "/{caterer_id}/status",
    response_model=CatererRead,
    status_code=status.HTTP_200_OK,
    summary="Update Caterer Status (Approve / Reject / Pending)"
)
def api_update_caterer_status(
    caterer_id: UUID,
    payload: CatererStatusPatch,
    db: Session = Depends(get_db)
):
    """
    Update only the status of a caterer.

    Allowed values:
    - pending
    - accepted
    - rejected
    """

    return update_caterer_status(
        db=db,
        caterer_id=caterer_id,
        new_status=payload.status
    )




@router.post(
    "/",
    response_model=CatererRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create Caterer with Image Upload"
)
def api_create_caterer(
    business_name: str = Form(...),
    phone_number: str = Form(...),
    email: Optional[str] = Form(None),
    password: Optional[str] = Form(None),

    description: Optional[str] = Form(None),

    cuisine_type: Optional[str] = Form(None),
    event_type: Optional[str] = Form(None),
    price_range: Optional[str] = Form(None),

    capacity_min: Optional[int] = Form(None),
    capacity_max: Optional[int] = Form(None),

    country: Optional[str] = Form(None),
    state: Optional[str] = Form(None),
    city: Optional[str] = Form(None),
    pincode: Optional[str] = Form(None),
    address_line: Optional[str] = Form(None),

    website: Optional[str] = Form(None),
    latitude: Optional[float] = Form(None),
    longitude: Optional[float] = Form(None),

    main_image: Optional[UploadFile] = File(None),
    photos: Optional[List[UploadFile]] = File(None),

    db: Session = Depends(get_db)
):
    try:

        # ---------------------------------
        # ✅ DEFINE VARIABLES FIRST
        # ---------------------------------
        main_image_url: Optional[str] = None
        gallery_urls: List[str] = []

        # ---------------------------------
        # ✅ Upload Main Image
        # ---------------------------------
        if main_image is not None:

            if not main_image.content_type.startswith("image/"):
                raise HTTPException(400, "Main file must be an image")

            try:
                main_image_url = upload_image_to_s3_create_caterer(main_image)
            except Exception as e:
                print("Main image upload failed:", e)
                raise HTTPException(500, "Failed to upload main image")

        # ---------------------------------
        # ✅ Upload Gallery Images
        # ---------------------------------
        if photos:

            for photo in photos:

                if not photo.content_type.startswith("image/"):
                    continue  # skip non-images safely

                try:
                    url = upload_image_to_s3_create_caterer(photo)
                    if url:
                        gallery_urls.append(url)

                except Exception as e:
                    print(f"S3 upload failed for gallery image: {e}")

        # ---------------------------------
        # ✅ Build Payload (STRINGS ONLY)
        # ---------------------------------
        payload = CatererCreate(
            business_name=business_name,
            phone_number=phone_number,
            email=email,
            password=password,
            description=description,
            cuisine_type=cuisine_type,
            event_type=event_type,
            price_range=price_range,
            capacity_min=capacity_min,
            capacity_max=capacity_max,
            country=country,
            state=state,
            city=city,
            pincode=pincode,
            address_line=address_line,
            website=website,
            latitude=latitude,
            longitude=longitude,

            # ⭐ Correct fields
            main_image=main_image_url,
            photo_folder_name=gallery_urls
        )

        # ---------------------------------
        # ✅ Save to DB
        # ---------------------------------
        return create_caterer(db=db, payload=payload)

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create caterer: {str(e)}"
        )



# =========================================================
# LIST CATERERS
# =========================================================
@router.get(
    "/",
    response_model=List[CatererRead]
)
def api_list_caterers(
    status: Optional[CatererStatus] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    return list_caterers(
        db=db,
        status=status,
        skip=skip,
        limit=limit
    )






# =========================================================
# 🔥 SEARCH BY LOCATION (STATIC ROUTE — MUST BE ABOVE /{id})
# =========================================================
@router.get(
    "/by-location",
    response_model=List[CatererListResponse],
    summary="Search caterers by location with filters"
)
def api_get_caterers_by_location(
    location: str = Query(
        ...,
        min_length=2,
        max_length=100,
        example="Hyderabad"
    ),

    # ✅ FILTERS
    event_types: Optional[List[str]] = Query(
        default=None,
        example=["Wedding", "Corporate"]
    ),

    cuisines: Optional[List[str]] = Query(
        default=None,
        example=["South Indian", "North Indian"]
    ),

    min_rating: Optional[float] = Query(
        default=None,
        ge=1,
        le=5,
        example=4
    ),

    # ✅ PAGINATION
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=10),

    db: Session = Depends(get_db)
):
    return get_caterers_by_location(
        db=db,
        location=location,
        page=page,
        limit=limit,
        event_types=event_types,
        cuisines=cuisines,
        min_rating=min_rating
    )

# =========================================================
# BULK UPLOAD
# =========================================================
@router.post(
    "/bulk-upload",
    response_model=CatererBulkUploadResponse,
    status_code=status.HTTP_201_CREATED
)
def api_bulk_upload_caterers(
    file: UploadFile = File(...),
    country: str = Form(...),
    state: Optional[str] = Form(None),
    city: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    return bulk_upload_caterers(
        db=db,
        file=file,
        country=country,
        state=state,
        city=city
    )


# =========================================================
# GET CATERER BY ID  ⚠️ ALWAYS KEEP DYNAMIC ROUTES LAST
# =========================================================
@router.get(
    "/{caterer_id}",
    response_model=CatererRead
)
def api_get_caterer(
    caterer_id: UUID,
    db: Session = Depends(get_db)
):
    return get_caterer_by_id(db, caterer_id)


# =========================================================
# UPDATE CATERER
# =========================================================
@router.put(
    "/{caterer_id}",
    response_model=CatererRead
)
def api_update_caterer(
    caterer_id: UUID,
    payload: CatererUpdate,
    db: Session = Depends(get_db)
):
    return update_caterer(db, caterer_id, payload)



@router.put("/{caterer_id}/main-image", response_model=CatererImageResponse)
def upload_main_image(
    caterer_id: UUID,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    caterer = upload_or_update_caterer_main_image(
        db=db,
        caterer_id=caterer_id,
        file=file
    )

    return caterer
