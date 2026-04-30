from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from schema.message.message import MessageCreate, MessageResponse
from service.message.message import MessageService
from config.db.session import get_db


router = APIRouter(
    prefix="/messages",
    tags=["Messages"]
)


@router.post(
    "/",
    response_model=MessageResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Send a message to a caterer"
)
def send_message(
    message_in: MessageCreate,
    db: Session = Depends(get_db)
):
    """
    Send a message from a user to a caterer.
    Saves message to DB and sends email to caterer via Brevo.
    """

    try:
        message = MessageService.send_message(db, message_in)
        return message

    except ValueError as e:
        # Known validation errors
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    except Exception as e:
        # Unexpected errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send message: {str(e)}"
        )
