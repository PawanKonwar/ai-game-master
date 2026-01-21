from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from game_agent import game_master

app = FastAPI(title="AI Game Master API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins like ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)


class SceneRequest(BaseModel):
    """Request model for scene generation"""
    prompt: str
    include_dice_rolls: bool = False


@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "AI Game Master API is running"}


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


@app.get("/test-scene")
async def test_scene():
    """Test endpoint that returns a sample game scene"""
    sample_scene = {
        "scene_id": "test_scene_001",
        "title": "The Mysterious Tavern",
        "description": "You find yourself in a dimly lit tavern. The air is thick with the smell of ale and roasted meat. A mysterious figure sits in the corner, watching you intently.",
        "characters": [
            {
                "name": "Mysterious Stranger",
                "role": "NPC",
                "description": "A cloaked figure with piercing eyes"
            }
        ],
        "locations": [
            {
                "name": "Main Hall",
                "description": "The main area of the tavern with tables and a bar"
            },
            {
                "name": "Corner Table",
                "description": "A secluded table in the corner where the stranger sits"
            }
        ],
        "items": [
            {
                "name": "Old Map",
                "description": "A weathered map with strange markings"
            }
        ],
        "actions": [
            "Approach the stranger",
            "Order a drink at the bar",
            "Examine the tavern more closely"
        ]
    }
    return JSONResponse(content=sample_scene)


@app.post("/generate-scene")
async def generate_scene(request: SceneRequest):
    """
    Generate a game scene based on a prompt using the AI game master agent.
    
    Args:
        request: JSON body containing a "prompt" field
        
    Returns:
        JSON response with the generated scene
    """
    # Validate that prompt is provided and not empty
    if not request.prompt or not request.prompt.strip():
        raise HTTPException(
            status_code=400,
            detail="Prompt is required and cannot be empty"
        )
    
    try:
        # Generate the scene using the game agent
        scene_text = game_master.generate_scene(
            request.prompt, 
            include_dice_rolls=request.include_dice_rolls
        )
        
        # Return the generated scene
        return JSONResponse(content={
            "success": True,
            "prompt": request.prompt,
            "include_dice_rolls": request.include_dice_rolls,
            "scene": scene_text
        })
    except Exception as e:
        # Handle any errors from the game agent
        raise HTTPException(
            status_code=500,
            detail=f"Error generating scene: {str(e)}"
        )
