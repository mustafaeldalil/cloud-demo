import os
import json
import time
import jwt
import boto3
import httpx
import psycopg2
from datetime import datetime
from typing import Optional
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from anthropic import Anthropic
from supabase import create_client

load_dotenv()

app = FastAPI(title="Cloud Demo API")

# CORS configuration
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize clients (with error handling for missing env vars)
supabase = None
try:
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_KEY")
    if supabase_url and supabase_key:
        supabase = create_client(supabase_url, supabase_key)
except Exception as e:
    print(f"Warning: Could not initialize Supabase client: {e}")

anthropic_client = None
try:
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    if anthropic_key and anthropic_key != "sk-ant-api03-...":
        anthropic_client = Anthropic(api_key=anthropic_key)
except Exception as e:
    print(f"Warning: Could not initialize Anthropic client: {e}")

# R2 client (S3-compatible)
r2_client = None
try:
    if os.getenv("R2_ACCESS_KEY_ID"):
        r2_client = boto3.client(
            "s3",
            endpoint_url=os.getenv("R2_ENDPOINT"),
            aws_access_key_id=os.getenv("R2_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("R2_SECRET_ACCESS_KEY"),
            region_name="auto",
        )
except Exception as e:
    print(f"Warning: Could not initialize R2 client: {e}")


# JWT verification
async def verify_token(authorization: Optional[str] = Header(None)) -> dict:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")
    
    token = authorization.split(" ")[1]
    
    try:
        # Fetch Supabase JWT secret (in production, cache this)
        jwt_secret = os.getenv("SUPABASE_JWT_SECRET")
        if jwt_secret:
            payload = jwt.decode(token, jwt_secret, algorithms=["HS256"], audience="authenticated")
        else:
            # If no secret configured, just decode without verification (for demo)
            payload = jwt.decode(token, options={"verify_signature": False})
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")


# Request models
class ChatRequest(BaseModel):
    message: str


# Health check
@app.get("/")
async def root():
    return {"status": "ok", "service": "Cloud Demo API"}


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "supabase": supabase is not None,
            "anthropic": anthropic_client is not None,
            "r2": r2_client is not None,
        }
    }


# Test database connection
@app.get("/api/test/database")
async def test_database(user: dict = Depends(verify_token)):
    db_url = os.getenv("SUPABASE_DB_URL")
    if not db_url:
        raise HTTPException(status_code=500, detail="Database URL not configured")
    
    try:
        conn = psycopg2.connect(db_url)
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        cursor.execute("SELECT NOW();")
        server_time = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        
        return {
            "status": "success",
            "message": f"Connected to Postgres. Server time: {server_time}",
            "version": version[:50] + "..."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database connection failed: {str(e)}")


# Test R2 connection
@app.post("/api/test/r2")
async def test_r2(user: dict = Depends(verify_token)):
    if not r2_client:
        raise HTTPException(status_code=500, detail="R2 not configured")
    
    bucket = os.getenv("R2_BUCKET_NAME", "demo-models")
    test_key = f"test/{datetime.utcnow().isoformat()}.txt"
    test_content = f"Test upload at {datetime.utcnow().isoformat()}"
    
    try:
        # Upload test file
        r2_client.put_object(
            Bucket=bucket,
            Key=test_key,
            Body=test_content.encode(),
            ContentType="text/plain"
        )
        
        # Verify it exists
        response = r2_client.head_object(Bucket=bucket, Key=test_key)
        
        # Clean up
        r2_client.delete_object(Bucket=bucket, Key=test_key)
        
        return {
            "status": "success",
            "message": f"Successfully uploaded and deleted test file to R2 bucket '{bucket}'"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"R2 operation failed: {str(e)}")


# Chat with Claude
@app.post("/api/chat")
async def chat(request: ChatRequest, user: dict = Depends(verify_token)):
    if not anthropic_client:
        raise HTTPException(status_code=500, detail="Anthropic API not configured")
    
    try:
        message = anthropic_client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=1024,
            messages=[
                {"role": "user", "content": request.message}
            ]
        )
        
        response_text = message.content[0].text
        
        # Log to database if available
        if supabase:
            try:
                supabase.table("chat_logs").insert({
                    "user_id": user.get("sub"),
                    "message": request.message,
                    "response": response_text,
                }).execute()
            except:
                pass  # Don't fail if logging fails
        
        return {
            "response": response_text,
            "model": "claude-3-haiku-20240307",
            "usage": {
                "input_tokens": message.usage.input_tokens,
                "output_tokens": message.usage.output_tokens
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Claude API error: {str(e)}")


# Metabase embed URL generation
@app.get("/api/metabase/embed/{dashboard_id}")
async def get_metabase_embed(dashboard_id: int, user: dict = Depends(verify_token)):
    metabase_url = os.getenv("METABASE_URL")
    metabase_secret = os.getenv("METABASE_SECRET_KEY")
    
    if not metabase_url or not metabase_secret:
        raise HTTPException(status_code=500, detail="Metabase not configured")
    
    try:
        # Create signed JWT for Metabase embed
        payload = {
            "resource": {"dashboard": dashboard_id},
            "params": {},
            "exp": int(time.time()) + 600  # 10 minute expiry
        }
        
        token = jwt.encode(payload, metabase_secret, algorithm="HS256")
        embed_url = f"{metabase_url}/embed/dashboard/{token}#bordered=true&titled=true"
        
        return {"embed_url": embed_url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate embed URL: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
