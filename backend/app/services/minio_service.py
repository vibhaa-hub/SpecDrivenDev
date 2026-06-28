from minio import Minio
import os
from fastapi import HTTPException, UploadFile
import uuid

# MinIO Configuration
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "localhost:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minioadmin")
BUCKET_NAME = "receipts"

minio_client = Minio(
    MINIO_ENDPOINT,
    access_key=MINIO_ACCESS_KEY,
    secret_key=MINIO_SECRET_KEY,
    secure=False
)

def ensure_bucket():
    if not minio_client.bucket_exists(BUCKET_NAME):
        minio_client.make_bucket(BUCKET_NAME)

def upload_receipt(file: UploadFile) -> str:
    ensure_bucket()
    # Generate unique filename
    ext = file.filename.split(".")[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    
    minio_client.put_object(
        BUCKET_NAME, 
        filename, 
        file.file, 
        length=-1, # Stream upload
        content_type=file.content_type
    )
    
    # Return a URL that can be used to access the file
    # In production, you'd use a presigned URL or a proxy
    return f"http://{MINIO_ENDPOINT}/{BUCKET_NAME}/{filename}"

def delete_receipt(receipt_url: str):
    ensure_bucket()
    filename = receipt_url.split("/")[-1]
    minio_client.remove_object(BUCKET_NAME, filename)

def get_receipt_url(receipt_url: str):
    # Logic to return the file or a presigned URL
    # For simplicity, we return the URL.
    return receipt_url
