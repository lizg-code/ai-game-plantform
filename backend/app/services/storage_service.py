import uuid
import boto3
from botocore.client import Config
from fastapi import UploadFile

from app.config import get_settings

settings = get_settings()


def get_s3_client():
    """Create and return an S3-compatible client for MinIO."""
    return boto3.client(
        "s3",
        endpoint_url=f"{'https' if settings.MINIO_USE_SSL else 'http'}://{settings.MINIO_ENDPOINT}",
        aws_access_key_id=settings.MINIO_ACCESS_KEY,
        aws_secret_access_key=settings.MINIO_SECRET_KEY,
        config=Config(signature_version="s3v4"),
        region_name="us-east-1",
    )


async def upload_file(file: UploadFile, folder: str = "uploads") -> str:
    """
    Upload a file to MinIO and return the public URL.
    """
    s3 = get_s3_client()

    # Generate unique filename
    ext = file.filename.split(".")[-1] if file.filename and "." in file.filename else "bin"
    unique_name = f"{folder}/{uuid.uuid4().hex}.{ext}"

    # Read file content
    content = await file.read()

    # Upload to MinIO
    content_type = file.content_type or "application/octet-stream"
    s3.put_object(
        Bucket=settings.MINIO_BUCKET,
        Key=unique_name,
        Body=content,
        ContentType=content_type,
    )

    # Return public URL
    public_url = f"{settings.MINIO_PUBLIC_URL}/{settings.MINIO_BUCKET}/{unique_name}"
    return public_url


def upload_html_content(html_content: str, filename: str) -> str:
    """
    Upload HTML content string to MinIO and return the public URL.
    Used by Agent service to upload generated game files.
    """
    s3 = get_s3_client()

    key = f"games/{filename}"
    s3.put_object(
        Bucket=settings.MINIO_BUCKET,
        Key=key,
        Body=html_content.encode("utf-8"),
        ContentType="text/html",
    )

    public_url = f"{settings.MINIO_PUBLIC_URL}/{settings.MINIO_BUCKET}/{key}"
    return public_url


def get_presigned_url(key: str, expires: int = 3600) -> str:
    """Generate a presigned URL for a MinIO object."""
    s3 = get_s3_client()
    return s3.generate_presigned_url(
        "get_object",
        Params={"Bucket": settings.MINIO_BUCKET, "Key": key},
        ExpiresIn=expires,
    )
