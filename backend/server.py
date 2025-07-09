from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pymongo import MongoClient
from typing import List, Optional
import os
import uuid
from datetime import datetime

app = FastAPI(title="Joatx - Household Repair Guide API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB connection
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/')
client = MongoClient(MONGO_URL)
db = client.joatx_db

# Models
class RepairStep(BaseModel):
    step_number: int
    title: str
    description: str
    safety_warning: Optional[str] = None
    image_url: Optional[str] = None

class RepairGuide(BaseModel):
    id: str
    title: str
    category: str
    difficulty: str
    estimated_time: str
    estimated_cost: str
    tools_needed: List[str]
    materials_needed: List[str]
    safety_tips: List[str]
    steps: List[RepairStep]
    created_at: datetime

class UserProgress(BaseModel):
    user_id: str
    guide_id: str
    current_step: int
    completed: bool

# Initialize with light bulb repair guide data
@app.on_event("startup")
async def startup_event():
    # Check if data already exists
    if db.repair_guides.count_documents({}) == 0:
        light_bulb_guide = {
            "id": str(uuid.uuid4()),
            "title": "Replace a Light Bulb",
            "category": "Electrical",
            "difficulty": "Easy",
            "estimated_time": "5-10 minutes",
            "estimated_cost": "$3-15",
            "tools_needed": [
                "Step ladder or stable chair",
                "Cloth or paper towel",
                "Flashlight (if needed)"
            ],
            "materials_needed": [
                "Replacement light bulb (check wattage)",
                "Gloves (optional)"
            ],
            "safety_tips": [
                "Turn off the light switch before starting",
                "Wait for the bulb to cool down if it was recently on",
                "Use a stable ladder or chair",
                "Never exceed the maximum wattage marked on the fixture",
                "If you're unsure about electrical work, call a professional"
            ],
            "steps": [
                {
                    "step_number": 1,
                    "title": "Turn Off Power",
                    "description": "Switch off the light at the wall switch. This is the most important safety step.",
                    "safety_warning": "Never attempt to change a bulb with power on",
                    "image_url": "https://images.unsplash.com/photo-1654117647413-0eb59cfe712d"
                },
                {
                    "step_number": 2,
                    "title": "Let Bulb Cool",
                    "description": "Wait 10-15 minutes for the bulb to cool down completely before handling.",
                    "safety_warning": "Hot bulbs can cause burns"
                },
                {
                    "step_number": 3,
                    "title": "Set Up Ladder",
                    "description": "Place a stable ladder or chair securely under the light fixture. Have someone hold it if needed.",
                    "safety_warning": "Ensure ladder is stable and on level ground"
                },
                {
                    "step_number": 4,
                    "title": "Remove Old Bulb",
                    "description": "Gently grip the bulb and turn counterclockwise (lefty-loosey) until it comes out. Use a cloth for better grip.",
                    "safety_warning": "Be gentle to avoid breaking the bulb"
                },
                {
                    "step_number": 5,
                    "title": "Check Wattage",
                    "description": "Check the wattage on the old bulb and fixture. Never exceed the maximum wattage.",
                    "safety_warning": "Wrong wattage can cause overheating and fires"
                },
                {
                    "step_number": 6,
                    "title": "Install New Bulb",
                    "description": "Screw the new bulb clockwise (righty-tighty) until snug. Don't overtighten.",
                    "safety_warning": "Overtightening can break the bulb or fixture"
                },
                {
                    "step_number": 7,
                    "title": "Test the Light",
                    "description": "Turn the power back on and test the light. If it doesn't work, check the bulb is properly screwed in.",
                    "safety_warning": "If light still doesn't work, there may be an electrical issue"
                }
            ],
            "created_at": datetime.now()
        }
        db.repair_guides.insert_one(light_bulb_guide)

# API Routes
@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "service": "Joatx API"}

@app.get("/api/guides")
async def get_all_guides():
    guides = list(db.repair_guides.find({}, {"_id": 0}))
    return guides

@app.get("/api/guides/{guide_id}")
async def get_guide(guide_id: str):
    guide = db.repair_guides.find_one({"id": guide_id}, {"_id": 0})
    if not guide:
        raise HTTPException(status_code=404, detail="Guide not found")
    return guide

@app.get("/api/categories")
async def get_categories():
    categories = db.repair_guides.distinct("category")
    return categories

@app.get("/api/guides/category/{category}")
async def get_guides_by_category(category: str):
    guides = list(db.repair_guides.find({"category": category}, {"_id": 0}))
    return guides

@app.post("/api/progress")
async def update_progress(progress: UserProgress):
    existing = db.user_progress.find_one({
        "user_id": progress.user_id,
        "guide_id": progress.guide_id
    })
    
    if existing:
        db.user_progress.update_one(
            {"user_id": progress.user_id, "guide_id": progress.guide_id},
            {"$set": progress.dict()}
        )
    else:
        db.user_progress.insert_one(progress.dict())
    
    return {"message": "Progress updated successfully"}

@app.get("/api/progress/{user_id}/{guide_id}")
async def get_progress(user_id: str, guide_id: str):
    progress = db.user_progress.find_one({
        "user_id": user_id,
        "guide_id": guide_id
    }, {"_id": 0})
    
    if not progress:
        return {"user_id": user_id, "guide_id": guide_id, "current_step": 0, "completed": False}
    
    return progress

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)