from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from pymongo import MongoClient
from typing import List, Optional
import os
import uuid
from datetime import datetime
import base64
from PIL import Image
import io
import json

app = FastAPI(title="Joatx - AI-Powered Household Repair Assistant")

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
class RepairAnalysis(BaseModel):
    problem_identified: str
    difficulty_level: str
    repair_type: str
    can_diy: bool
    estimated_time: str
    estimated_cost: str
    tools_needed: List[str]
    materials_needed: List[str]
    safety_warnings: List[str]
    steps: List[dict]
    professional_needed: bool
    professional_type: str

class LocationRequest(BaseModel):
    latitude: float
    longitude: float
    problem_type: str

class NearbyService(BaseModel):
    name: str
    address: str
    phone: str
    rating: float
    distance: str
    type: str
    specialties: List[str]

# Mock AI Analysis Functions
def analyze_image_mock(image_data: bytes) -> RepairAnalysis:
    """Mock AI analysis - simulates OpenAI Vision analysis"""
    
    # Simulate different types of repairs based on image characteristics
    mock_analyses = {
        "electrical": {
            "problem_identified": "Broken light fixture with damaged wiring",
            "difficulty_level": "Medium",
            "repair_type": "Electrical",
            "can_diy": False,
            "estimated_time": "2-3 hours",
            "estimated_cost": "$50-150",
            "tools_needed": ["Wire strippers", "Electrical tester", "Screwdriver set", "Wire nuts"],
            "materials_needed": ["Electrical wire", "New fixture", "Wire nuts", "Electrical tape"],
            "safety_warnings": [
                "Turn off power at circuit breaker before starting",
                "Test wires with electrical tester to ensure power is off",
                "If you're unsure about electrical work, hire a licensed electrician",
                "Wet hands and electrical work don't mix"
            ],
            "steps": [
                {"step": 1, "title": "Turn Off Power", "description": "Switch off the circuit breaker for this fixture", "safety_critical": True},
                {"step": 2, "title": "Test Wires", "description": "Use electrical tester to confirm power is off", "safety_critical": True},
                {"step": 3, "title": "Remove Old Fixture", "description": "Carefully disconnect and remove the damaged fixture"},
                {"step": 4, "title": "Install New Fixture", "description": "Connect new fixture following manufacturer instructions"},
                {"step": 5, "title": "Test Installation", "description": "Turn power back on and test the new fixture"}
            ],
            "professional_needed": True,
            "professional_type": "electrician"
        },
        "plumbing": {
            "problem_identified": "Leaky faucet with worn washers",
            "difficulty_level": "Easy",
            "repair_type": "Plumbing",
            "can_diy": True,
            "estimated_time": "30-45 minutes",
            "estimated_cost": "$5-25",
            "tools_needed": ["Adjustable wrench", "Screwdriver", "Pliers"],
            "materials_needed": ["Faucet washers", "O-rings", "Plumber's grease"],
            "safety_warnings": [
                "Turn off water supply before starting",
                "Have towels ready for water cleanup",
                "If pipes are old, consider calling a plumber"
            ],
            "steps": [
                {"step": 1, "title": "Turn Off Water", "description": "Shut off water supply under sink", "safety_critical": True},
                {"step": 2, "title": "Remove Handle", "description": "Remove faucet handle and packing nut"},
                {"step": 3, "title": "Replace Washers", "description": "Remove old washers and install new ones"},
                {"step": 4, "title": "Reassemble", "description": "Put everything back together in reverse order"},
                {"step": 5, "title": "Test Repair", "description": "Turn water back on and check for leaks"}
            ],
            "professional_needed": False,
            "professional_type": "plumber"
        },
        "appliance": {
            "problem_identified": "Dishwasher not draining properly",
            "difficulty_level": "Medium",
            "repair_type": "Appliance",
            "can_diy": True,
            "estimated_time": "1-2 hours",
            "estimated_cost": "$10-50",
            "tools_needed": ["Screwdriver", "Pliers", "Bucket", "Towels"],
            "materials_needed": ["Replacement filter", "Drain cleaner", "New gaskets if needed"],
            "safety_warnings": [
                "Disconnect power before starting",
                "Water may spill during repair",
                "Check warranty before attempting repair"
            ],
            "steps": [
                {"step": 1, "title": "Disconnect Power", "description": "Unplug dishwasher or turn off circuit breaker"},
                {"step": 2, "title": "Remove Bottom Rack", "description": "Take out the bottom dish rack"},
                {"step": 3, "title": "Clean Filter", "description": "Remove and clean the drain filter"},
                {"step": 4, "title": "Check Drain Hose", "description": "Inspect drain hose for clogs"},
                {"step": 5, "title": "Reassemble and Test", "description": "Put everything back and run a test cycle"}
            ],
            "professional_needed": False,
            "professional_type": "appliance_repair"
        }
    }
    
    # Simulate image analysis by returning a random analysis
    import random
    analysis_type = random.choice(list(mock_analyses.keys()))
    return RepairAnalysis(**mock_analyses[analysis_type])

def get_nearby_services_mock(lat: float, lng: float, problem_type: str) -> List[NearbyService]:
    """Mock geolocation services - simulates Google Places API"""
    
    mock_services = {
        "electrician": [
            {
                "name": "Quick Fix Electrical",
                "address": "123 Main St, Your City",
                "phone": "(555) 123-4567",
                "rating": 4.8,
                "distance": "0.5 miles",
                "type": "electrician",
                "specialties": ["Residential wiring", "Lighting repair", "Circuit breakers"]
            },
            {
                "name": "Spark Masters Electric",
                "address": "456 Oak Ave, Your City",
                "phone": "(555) 987-6543",
                "rating": 4.6,
                "distance": "1.2 miles",
                "type": "electrician",
                "specialties": ["Emergency repairs", "Panel upgrades", "Outlet installation"]
            }
        ],
        "plumber": [
            {
                "name": "Rapid Plumbing Services",
                "address": "789 Pine St, Your City",
                "phone": "(555) 456-7890",
                "rating": 4.9,
                "distance": "0.8 miles",
                "type": "plumber",
                "specialties": ["Leak repair", "Drain cleaning", "Faucet installation"]
            },
            {
                "name": "All-Day Plumbing",
                "address": "321 Elm Dr, Your City",
                "phone": "(555) 234-5678",
                "rating": 4.7,
                "distance": "1.5 miles",
                "type": "plumber",
                "specialties": ["24/7 emergency", "Pipe repair", "Water heater service"]
            }
        ],
        "hardware_store": [
            {
                "name": "Home Depot",
                "address": "100 Commerce Blvd, Your City",
                "phone": "(555) 111-2222",
                "rating": 4.3,
                "distance": "2.1 miles",
                "type": "hardware_store",
                "specialties": ["Tools", "Electrical supplies", "Plumbing parts"]
            },
            {
                "name": "Ace Hardware",
                "address": "555 Market St, Your City",
                "phone": "(555) 333-4444",
                "rating": 4.5,
                "distance": "1.8 miles",
                "type": "hardware_store",
                "specialties": ["Local expertise", "Specialty tools", "Repair parts"]
            }
        ],
        "appliance_repair": [
            {
                "name": "Appliance Doctor",
                "address": "777 Service Rd, Your City",
                "phone": "(555) 777-8888",
                "rating": 4.8,
                "distance": "1.0 miles",
                "type": "appliance_repair",
                "specialties": ["Dishwashers", "Refrigerators", "Washing machines"]
            }
        ]
    }
    
    # Return relevant services based on problem type
    services = []
    if problem_type in mock_services:
        services.extend(mock_services[problem_type])
    
    # Always include hardware stores for parts
    services.extend(mock_services["hardware_store"])
    
    return [NearbyService(**service) for service in services]

# Initialize with sample data
@app.on_event("startup")
async def startup_event():
    # Check if repair analyses collection exists
    if db.repair_analyses.count_documents({}) == 0:
        print("Database initialized for repair analyses")

# API Routes
@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "service": "Joatx AI Repair Assistant"}

@app.post("/api/analyze-image")
async def analyze_repair_image(file: UploadFile = File(...)):
    """Analyze uploaded image for repair guidance"""
    try:
        # Read and validate image
        image_data = await file.read()
        if len(image_data) == 0:
            raise HTTPException(status_code=400, detail="Empty file uploaded")
        
        # Validate image format
        try:
            img = Image.open(io.BytesIO(image_data))
            img.verify()
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid image format")
        
        # Perform AI analysis (mock)
        analysis = analyze_image_mock(image_data)
        
        # Save analysis to database
        analysis_record = {
            "id": str(uuid.uuid4()),
            "analysis": analysis.dict(),
            "timestamp": datetime.now(),
            "image_size": len(image_data)
        }
        
        db.repair_analyses.insert_one(analysis_record)
        
        return {
            "analysis_id": analysis_record["id"],
            "analysis": analysis.dict(),
            "message": "Image analyzed successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.post("/api/find-nearby")
async def find_nearby_services(location: LocationRequest):
    """Find nearby services based on location and problem type"""
    try:
        # Get nearby services (mock)
        services = get_nearby_services_mock(
            location.latitude, 
            location.longitude, 
            location.problem_type
        )
        
        # Save search to database
        search_record = {
            "id": str(uuid.uuid4()),
            "location": {"lat": location.latitude, "lng": location.longitude},
            "problem_type": location.problem_type,
            "results_count": len(services),
            "timestamp": datetime.now()
        }
        
        db.location_searches.insert_one(search_record)
        
        return {
            "search_id": search_record["id"],
            "services": [service.dict() for service in services],
            "total_found": len(services)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Location search failed: {str(e)}")

@app.get("/api/analysis/{analysis_id}")
async def get_analysis(analysis_id: str):
    """Get stored analysis by ID"""
    analysis = db.repair_analyses.find_one({"id": analysis_id}, {"_id": 0})
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return analysis

@app.get("/api/guides")
async def get_all_guides():
    """Get all repair guides (backward compatibility)"""
    guides = list(db.repair_guides.find({}, {"_id": 0}))
    return guides

@app.get("/api/guides/{guide_id}")
async def get_guide(guide_id: str):
    """Get specific repair guide (backward compatibility)"""
    guide = db.repair_guides.find_one({"id": guide_id}, {"_id": 0})
    if not guide:
        raise HTTPException(status_code=404, detail="Guide not found")
    return guide

@app.post("/api/emergency-contact")
async def emergency_contact(contact_request: dict):
    """Handle emergency contact requests"""
    try:
        # Save emergency request
        emergency_record = {
            "id": str(uuid.uuid4()),
            "problem_type": contact_request.get("problem_type"),
            "urgency": contact_request.get("urgency", "medium"),
            "user_location": contact_request.get("location"),
            "timestamp": datetime.now(),
            "status": "pending"
        }
        
        db.emergency_contacts.insert_one(emergency_record)
        
        return {
            "request_id": emergency_record["id"],
            "message": "Emergency contact request logged",
            "estimated_response": "15-30 minutes"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Emergency contact failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)