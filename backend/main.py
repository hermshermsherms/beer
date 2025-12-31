from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional, List
import os
from datetime import datetime
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Beer App API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Supabase setup
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_ANON_KEY")

if not supabase_url or not supabase_key:
    raise ValueError("SUPABASE_URL and SUPABASE_ANON_KEY must be set in .env file")

try:
    supabase: Client = create_client(supabase_url, supabase_key)
except Exception as e:
    print(f"Error connecting to Supabase: {e}")
    # For now, we'll create a mock client for testing
    supabase = None

security = HTTPBearer()

class UserCreate(BaseModel):
    username: str
    password: str
    name: str

class UserLogin(BaseModel):
    username: str
    password: str

class BeerPost(BaseModel):
    note: str

@app.post("/api/register")
async def register(user: UserCreate):
    try:
        # Create user account
        response = supabase.auth.sign_up({
            "email": f"{user.username}@beerapp.local",
            "password": user.password,
            "options": {
                "data": {
                    "username": user.username,
                    "name": user.name
                }
            }
        })
        
        if response.user:
            # Insert user profile
            supabase.table("users").insert({
                "id": response.user.id,
                "username": user.username,
                "name": user.name
            }).execute()
            
            return {"message": "User registered successfully", "user_id": response.user.id}
        else:
            raise HTTPException(status_code=400, detail="Registration failed")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/login")
async def login(user: UserLogin):
    try:
        response = supabase.auth.sign_in_with_password({
            "email": f"{user.username}@beerapp.local",
            "password": user.password
        })
        
        if response.session:
            return {
                "access_token": response.session.access_token,
                "user_id": response.user.id
            }
        else:
            raise HTTPException(status_code=401, detail="Invalid credentials")
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid credentials")

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        user = supabase.auth.get_user(credentials.credentials)
        return user.user
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.post("/api/beers")
async def post_beer(
    note: str = Form(...),
    image: UploadFile = File(...),
    current_user = Depends(get_current_user)
):
    try:
        # Upload image to Supabase storage
        file_content = await image.read()
        file_name = f"{current_user.id}_{datetime.now().isoformat()}_{image.filename}"
        
        storage_response = supabase.storage.from_("beer-images").upload(
            file_name, file_content
        )
        
        if storage_response.error:
            raise HTTPException(status_code=400, detail="Image upload failed")
        
        # Get public URL for the image
        image_url = supabase.storage.from_("beer-images").get_public_url(file_name)
        
        # Insert beer post
        beer_response = supabase.table("beers").insert({
            "user_id": current_user.id,
            "image_url": image_url.data.get("publicUrl"),
            "note": note,
            "created_at": datetime.now().isoformat()
        }).execute()
        
        return {"message": "Beer posted successfully", "beer_id": beer_response.data[0]["id"]}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/beers/my")
async def get_my_beers(current_user = Depends(get_current_user)):
    try:
        response = supabase.table("beers").select("*").eq("user_id", current_user.id).order("created_at", desc=True).execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/beers/all")
async def get_all_beers():
    try:
        response = supabase.table("beers").select("""
            *,
            users!beers_user_id_fkey(name)
        """).order("created_at", desc=True).execute()
        
        # Format the response to include user name
        beers = []
        for beer in response.data:
            beers.append({
                **beer,
                "user_name": beer["users"]["name"] if beer["users"] else "Unknown"
            })
        
        return beers
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/api/beers/{beer_id}")
async def delete_beer(beer_id: str, current_user = Depends(get_current_user)):
    try:
        # Verify the beer belongs to the current user
        beer_response = supabase.table("beers").select("*").eq("id", beer_id).eq("user_id", current_user.id).execute()
        
        if not beer_response.data:
            raise HTTPException(status_code=404, detail="Beer not found or not owned by user")
        
        # Delete the beer
        supabase.table("beers").delete().eq("id", beer_id).execute()
        
        return {"message": "Beer deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/leaderboard")
async def get_leaderboard():
    try:
        # Get beer counts by user and month
        response = supabase.rpc("get_monthly_beer_counts").execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)