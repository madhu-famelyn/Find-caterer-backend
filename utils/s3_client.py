import os
import boto3
from dotenv import load_dotenv

load_dotenv()

s3_client = boto3.client(
    "s3",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_REGION"),
)

BUCKET_NAME = os.getenv("AWS_BUCKET_NAME")


def test_s3_upload():
    s3_client.put_object(
        Bucket=BUCKET_NAME,
        Key="test/connection-check.txt",
        Body=b"S3 connection successful",
        ContentType="text/plain",
    )
