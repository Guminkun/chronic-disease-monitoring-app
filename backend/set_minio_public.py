from minio import Minio
import json
from app.config import settings

def set_bucket_public():
    # Remove http/https from endpoint
    endpoint = settings.MINIO_ENDPOINT
    if endpoint.startswith("http://"):
        endpoint = endpoint.replace("http://", "")
    elif endpoint.startswith("https://"):
        endpoint = endpoint.replace("https://", "")
        
    client = Minio(
        endpoint,
        access_key=settings.MINIO_ACCESS_KEY,
        secret_key=settings.MINIO_SECRET_KEY,
        secure=settings.MINIO_SECURE
    )
    
    bucket_name = settings.MINIO_BUCKET_NAME
    
    if not client.bucket_exists(bucket_name):
        print(f"Bucket {bucket_name} does not exist. Creating...")
        client.make_bucket(bucket_name)
    
    policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {"AWS": ["*"]},
                "Action": ["s3:GetObject"],
                "Resource": [f"arn:aws:s3:::{bucket_name}/*"]
            }
        ]
    }
    
    try:
        client.set_bucket_policy(bucket_name, json.dumps(policy))
        print(f"Successfully set bucket {bucket_name} policy to public read.")
    except Exception as e:
        print(f"Error setting policy: {e}")

if __name__ == "__main__":
    set_bucket_public()
