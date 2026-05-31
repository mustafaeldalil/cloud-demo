"""
Upload Model to R2 - Runs after ML training
Demonstrates: GitHub Actions → Cloudflare R2 connection
"""

import os
import boto3
from datetime import datetime

def upload_to_r2():
    print(f"[{datetime.utcnow().isoformat()}] Uploading model to R2...")
    
    # Check required env vars
    required = ["R2_ACCESS_KEY_ID", "R2_SECRET_ACCESS_KEY", "R2_ENDPOINT", "R2_BUCKET_NAME"]
    missing = [v for v in required if not os.getenv(v)]
    
    if missing:
        print(f"⚠ Missing environment variables: {missing}")
        print("  Skipping R2 upload (this is OK for local testing)")
        return True
    
    try:
        # Initialize R2 client
        r2 = boto3.client(
            "s3",
            endpoint_url=os.getenv("R2_ENDPOINT"),
            aws_access_key_id=os.getenv("R2_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("R2_SECRET_ACCESS_KEY"),
            region_name="auto",
        )
        
        bucket = os.getenv("R2_BUCKET_NAME")
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        
        # Upload model file
        model_path = "artifacts/model_latest.pkl"
        if os.path.exists(model_path):
            r2.upload_file(
                model_path,
                bucket,
                f"models/model_{timestamp}.pkl"
            )
            # Also upload as "latest"
            r2.upload_file(
                model_path,
                bucket,
                "models/model_latest.pkl"
            )
            print(f"✓ Uploaded model to R2: models/model_{timestamp}.pkl")
        
        # Upload metadata
        metadata_path = "artifacts/model_metadata.json"
        if os.path.exists(metadata_path):
            r2.upload_file(
                metadata_path,
                bucket,
                f"models/metadata_{timestamp}.json"
            )
            r2.upload_file(
                metadata_path,
                bucket,
                "models/metadata_latest.json"
            )
            print(f"✓ Uploaded metadata to R2")
        
        print(f"[{datetime.utcnow().isoformat()}] R2 upload completed")
        return True
        
    except Exception as e:
        print(f"✗ R2 upload failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = upload_to_r2()
    exit(0 if success else 1)
