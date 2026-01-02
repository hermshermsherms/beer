from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import os
from datetime import datetime

app = FastAPI(title="Beer App API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for your domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Environment variables for Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")

# Mock data storage (fallback if Supabase not available)
users_db = {}
beers_db = []
sessions = {}  # Store active sessions
current_user_id = None

# Try to import Supabase, fallback to mock if not available
try:
    from supabase import create_client, Client
    if SUPABASE_URL and SUPABASE_ANON_KEY:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
        USE_SUPABASE = True
    else:
        supabase = None
        USE_SUPABASE = False
except ImportError:
    supabase = None
    USE_SUPABASE = False

class UserCreate(BaseModel):
    username: str
    password: str
    name: str

class UserLogin(BaseModel):
    username: str
    password: str

def get_current_user_from_token(authorization: str = None):
    """Extract user ID from Authorization header"""
    if not authorization:
        return None
    
    if authorization.startswith('Bearer '):
        token = authorization[7:]  # Remove 'Bearer ' prefix
        return sessions.get(token)
    
    return None

@app.post("/api/register")
async def register(user: UserCreate):
    global current_user_id
    
    if USE_SUPABASE:
        try:
            # Create user with Supabase Auth
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
                
                return {"message": "User registered successfully", "user_id": response.user.id, "access_token": "supabase_token"}
        except Exception as e:
            # Fallback to mock
            pass
    
    # Mock fallback
    user_id = f"user_{len(users_db) + 1}"
    users_db[user_id] = {
        "id": user_id,
        "username": user.username,
        "name": user.name,
        "password": user.password
    }
    current_user_id = user_id
    return {"message": "User registered successfully (mock)", "user_id": user_id, "access_token": f"token_{user_id}"}

@app.post("/api/login")
async def login(user: UserLogin):
    global current_user_id
    
    if USE_SUPABASE:
        try:
            # Try Supabase authentication
            response = supabase.auth.sign_in_with_password({
                "email": f"{user.username}@beerapp.local",
                "password": user.password
            })
            
            if response.session:
                user_id = response.user.id
                token = response.session.access_token
                sessions[token] = user_id
                current_user_id = user_id
                return {
                    "access_token": token,
                    "user_id": user_id,
                    "message": "Logged in with Supabase"
                }
        except Exception as e:
            print(f"Supabase login failed: {e}")
            # Fall through to mock authentication
    
    # Mock authentication fallback
    for uid, u in users_db.items():
        if u["username"] == user.username and u["password"] == user.password:
            token = f"mock_token_{uid}"
            sessions[token] = uid
            current_user_id = uid
            return {
                "access_token": token, 
                "user_id": uid,
                "message": "Logged in with mock data"
            }
    
    raise HTTPException(status_code=401, detail="Invalid credentials")

@app.post("/api/beers")
async def post_beer(
    note: str = Form(...), 
    image: UploadFile = File(...),
    authorization: str = None
):
    user_id = get_current_user_from_token(authorization)
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # Get user name for display
    user_name = "Unknown User"
    if user_id in users_db:
        user_name = users_db[user_id]["name"]
    
    beer = {
        "id": f"beer_{len(beers_db) + 1}",
        "user_id": user_id,
        "image_url": f"https://via.placeholder.com/80x80?text=🍺",
        "note": note,
        "created_at": datetime.now().isoformat(),
        "user_name": user_name
    }
    beers_db.append(beer)
    return {"message": "Beer posted successfully", "beer_id": beer["id"]}

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
    return [
        {
            "user_name": "John Doe",
            "monthly_data": [
                {"month": "2023-10", "total_drinks": 5},
                {"month": "2023-11", "total_drinks": 12},
                {"month": "2023-12", "total_drinks": 18}
            ]
        }
    ]