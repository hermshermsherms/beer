from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import os
from datetime import datetime
import json
import urllib.request
import urllib.parse
import uuid
import base64

app = FastAPI(title="Beer App API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Supabase configuration
SUPABASE_URL = os.environ.get('SUPABASE_URL')
SUPABASE_ANON_KEY = os.environ.get('SUPABASE_ANON_KEY')

if not SUPABASE_URL or not SUPABASE_ANON_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_ANON_KEY must be set")

# Mock data storage (in production, this would be your database)
users_db = {}
beers_db = []
current_user_id = None

def upload_image_to_supabase(image_content, filename, user_id):
    """Upload image to Supabase Storage and return public URL"""
    try:
        # Generate unique filename with proper extension
        file_ext = filename.split('.')[-1] if '.' in filename else 'jpg'
        unique_filename = f"{user_id}/{uuid.uuid4()}.{file_ext}"
        
        # Determine content type based on file extension
        content_type = 'image/jpeg'  # Default
        if file_ext.lower() in ['png']:
            content_type = 'image/png'
        elif file_ext.lower() in ['gif']:
            content_type = 'image/gif'
        elif file_ext.lower() in ['webp']:
            content_type = 'image/webp'
        
        print(f"Attempting to upload image: {unique_filename}, size: {len(image_content)} bytes, type: {content_type}")
        
        # Upload to Supabase Storage
        upload_req = urllib.request.Request(
            f"{SUPABASE_URL}/storage/v1/object/beer-images/{unique_filename}",
            data=image_content,
            headers={
                'Authorization': f'Bearer {SUPABASE_ANON_KEY}',
                'Content-Type': content_type,
                'apikey': SUPABASE_ANON_KEY
            },
            method='POST'
        )
        
        with urllib.request.urlopen(upload_req) as upload_response:
            upload_result = json.loads(upload_response.read().decode('utf-8'))
            print(f"Upload successful: {upload_result}")
        
        # Get public URL
        public_url = f"{SUPABASE_URL}/storage/v1/object/public/beer-images/{unique_filename}"
        
        return public_url
        
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8') if e.fp else str(e)
        print(f"HTTP Error uploading image: {e.code} - {e.reason}")
        print(f"Error response body: {error_body}")
        print(f"Upload URL: {SUPABASE_URL}/storage/v1/object/beer-images/{unique_filename}")
        # Return placeholder if upload fails
        return "https://via.placeholder.com/300x300/4A90E2/FFFFFF?text=🍺"
    except Exception as e:
        print(f"General error uploading image: {e}")
        print(f"Error type: {type(e)}")
        # Return placeholder if upload fails
        return "https://via.placeholder.com/300x300/4A90E2/FFFFFF?text=🍺"

class UserCreate(BaseModel):
    username: str
    password: str
    name: str

class UserLogin(BaseModel):
    username: str
    password: str

@app.post("/api/register")
async def register(user: UserCreate):
    global current_user_id
    user_id = f"user_{len(users_db) + 1}"
    users_db[user_id] = {
        "id": user_id,
        "username": user.username,
        "name": user.name,
        "password": user.password  # In production, this should be hashed
    }
    current_user_id = user_id
    return {"message": "User registered successfully", "user_id": user_id, "access_token": f"token_{user_id}"}

@app.post("/api/login")
async def login(user: UserLogin):
    global current_user_id
    for uid, u in users_db.items():
        if u["username"] == user.username and u["password"] == user.password:
            current_user_id = uid
            return {"access_token": f"token_{uid}", "user_id": uid}
    raise HTTPException(status_code=401, detail="Invalid credentials")

@app.post("/api/beers")
async def post_beer(
    note: str = Form(...),
    image: UploadFile = File(...)
):
    if not current_user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    if not note or len(note.strip()) == 0:
        raise HTTPException(status_code=400, detail="Note is required")
    
    if len(note) > 250:
        raise HTTPException(status_code=400, detail="Note must be 250 characters or less")
    
    # Read and upload image to Supabase Storage
    try:
        image_content = await image.read()
        image_url = upload_image_to_supabase(image_content, image.filename or "image.jpg", current_user_id)
    except Exception as e:
        print(f"Error processing image: {e}")
        raise HTTPException(status_code=500, detail="Failed to process image")
    
    beer = {
        "id": f"beer_{len(beers_db) + 1}",
        "user_id": current_user_id,
        "image_url": image_url,
        "note": note.strip(),
        "created_at": datetime.now().isoformat(),
        "user_name": users_db[current_user_id]["name"]
    }
    beers_db.append(beer)
    
    return {"message": "Beer posted successfully", "beer_id": beer["id"], "image_url": image_url}

@app.get("/api/beers/my")
async def get_my_beers():
    if not current_user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    user_beers = [beer for beer in beers_db if beer["user_id"] == current_user_id]
    return sorted(user_beers, key=lambda x: x["created_at"], reverse=True)

@app.get("/api/beers/all")
async def get_all_beers():
    return sorted(beers_db, key=lambda x: x["created_at"], reverse=True)

@app.delete("/api/beers/{beer_id}")
async def delete_beer(beer_id: str):
    if not current_user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    for i, beer in enumerate(beers_db):
        if beer["id"] == beer_id and beer["user_id"] == current_user_id:
            del beers_db[i]
            return {"message": "Beer deleted successfully"}
    
    raise HTTPException(status_code=404, detail="Beer not found")

@app.get("/api/leaderboard")
async def get_leaderboard():
    # Mock leaderboard data
    return [
        {
            "user_name": "John Doe",
            "monthly_data": [
                {"month": "2023-10", "total_drinks": 5},
                {"month": "2023-11", "total_drinks": 12},
                {"month": "2023-12", "total_drinks": 18}
            ]
        },
        {
            "user_name": "Jane Smith", 
            "monthly_data": [
                {"month": "2023-10", "total_drinks": 3},
                {"month": "2023-11", "total_drinks": 8},
                {"month": "2023-12", "total_drinks": 15}
            ]
        }
    ]

if __name__ == "__main__":
    import uvicorn
    print("Starting Beer App API on http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)