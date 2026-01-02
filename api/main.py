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

# Mock data storage (in production, use Supabase)
users_db = {}
beers_db = []
current_user_id = None

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
        "password": user.password
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
async def post_beer(note: str = Form(...), image: UploadFile = File(...)):
    if not current_user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    beer = {
        "id": f"beer_{len(beers_db) + 1}",
        "user_id": current_user_id,
        "image_url": f"https://via.placeholder.com/80x80?text=🍺",
        "note": note,
        "created_at": datetime.now().isoformat(),
        "user_name": users_db[current_user_id]["name"]
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