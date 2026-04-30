import os
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from models.message.message import Message
from models.user.user import User
from models.caterer.caterer import Caterer, CatererStatus
from schema.message.message import MessageCreate
from sib_api_v3_sdk import ApiClient, Configuration, TransactionalEmailsApi
from sib_api_v3_sdk.models.send_smtp_email import SendSmtpEmail


# -------------------------------------------------
# ENV
# -------------------------------------------------
load_dotenv()

BREVO_API_KEY = os.getenv("BREVO_API_KEY")
FROM_EMAIL = os.getenv("FROM_EMAIL", "noreply@fliplyn.com")
FROM_NAME = os.getenv("FROM_NAME", "Fliplyn Marketplace")


# -------------------------------------------------
# EMAIL SENDER
# -------------------------------------------------
def send_email_to_caterer(to_email: str, subject: str, html_content: str):
    """
    Sends transactional email to Caterer using Brevo.
    """

    if not BREVO_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Brevo API key is missing"
        )

    configuration = Configuration()
    configuration.api_key["api-key"] = BREVO_API_KEY

    api_client = ApiClient(configuration)
    api_instance = TransactionalEmailsApi(api_client)

    email = SendSmtpEmail(
        to=[{"email": to_email}],
        sender={"email": FROM_EMAIL, "name": FROM_NAME},
        subject=subject,
        html_content=html_content
    )

    try:
        api_instance.send_transac_email(email)

    except Exception as e:
        print(f"Email sending failed: {e}")

        # DO NOT crash message sending if email fails
        # Marketplace rule: message > email
        pass


# -------------------------------------------------
# MESSAGE SERVICE
# -------------------------------------------------
class MessageService:

    @staticmethod
    def send_message(db: Session, message_in: MessageCreate) -> Message:

        # -------------------------------------------------
        # Validate User
        # -------------------------------------------------
        user = db.query(User).filter(User.id == message_in.user_id).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User does not exist"
            )

        # -------------------------------------------------
        # Validate Caterer
        # -------------------------------------------------
        caterer = db.query(Caterer).filter(
            Caterer.id == message_in.caterer_id,
            Caterer.is_active.is_(True)
        ).first()

        if not caterer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Caterer does not exist or is inactive"
            )

        # 🚨 Optional but SMART:
        # Only allow accepted caterers
        if caterer.status != CatererStatus.accepted:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Caterer is not accepting messages yet"
            )

        # -------------------------------------------------
        # Create Message
        # -------------------------------------------------
        message = Message(
            user_id=message_in.user_id,
            caterer_id=message_in.caterer_id,
            email=message_in.email,
            user_full_name=message_in.user_full_name,
            user_phone_number=message_in.user_phone_number,
            message=message_in.message,
            sender_type="user"
        )

        db.add(message)
        db.commit()
        db.refresh(message)

        # -------------------------------------------------
        # Send Email Notification
        # -------------------------------------------------
        if caterer.email:

            subject = f"New message from {message_in.user_full_name}"

            html_content = f"""
            <h3>You received a new inquiry 🎉</h3>

            <p><strong>Name:</strong> {message_in.user_full_name}</p>
            <p><strong>Email:</strong> {message_in.email}</p>
            <p><strong>Phone:</strong> {message_in.user_phone_number}</p>

            <hr>

            <p><strong>Message:</strong></p>
            <p>{message_in.message}</p>

            <br>

            <p>Please respond to the customer as soon as possible.</p>

            <b>— Fliplyn Marketplace</b>
            """

            send_email_to_caterer(
                caterer.email,
                subject,
                html_content
            )

        return message
