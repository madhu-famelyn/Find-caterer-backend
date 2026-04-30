import os
import uuid
import requests
import boto3

AWS_REGION = os.getenv("AWS_REGION")
BUCKET_NAME = os.getenv("AWS_BUCKET_NAME")

s3_client = boto3.client(
    "s3",
    region_name=AWS_REGION,
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
)


def upload_google_image_to_s3(image_url: str) -> str:
    """
    Downloads an image from a Google-hosted URL
    uploads it to S3
    returns the S3 public URL
    """

    # 🔹 Download image
    response = requests.get(image_url, timeout=10)
    response.raise_for_status()

    # 🔹 Generate unique filename
    file_name = f"caterers/{uuid.uuid4()}.jpg"

    # 🔹 Upload to S3
    s3_client.put_object(
        Bucket=BUCKET_NAME,
        Key=file_name,
        Body=response.content,
        ContentType="image/jpeg",
    )

    # 🔹 Return S3 URL
    return f"https://{BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{file_name}"
