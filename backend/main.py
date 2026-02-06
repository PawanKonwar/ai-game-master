import sys
import time
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger
from pydantic import BaseModel

from game_agent import game_master

# Ensure logs directory exists for AI observability
Path("logs").mkdir(exist_ok=True)

# Configure Loguru for AI observability (structured, traceable logs)
logger.add(
    "logs/ai_observability_{time:YYYY-MM-DD}.log",
    rotation="1 day",
    retention="7 days",
    level="INFO",
    format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level} | {message}",
)
logger.add(
    sys.stderr,
    level="INFO",
    format="<green>{time:HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <level>{message}</level>",
)

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

    request_id = f"scene_{int(time.time() * 1000)}"
    t_start = time.perf_counter()

    logger.info(
        "llm_request_start | request_id={} | prompt_len={} | include_dice_rolls={}",
        request_id,
        len(request.prompt),
        request.include_dice_rolls,
    )

    try:
        # Generate the scene using the game agent (retrieval + LLM call inside)
        scene_text = game_master.generate_scene(
            request.prompt,
            include_dice_rolls=request.include_dice_rolls,
        )

        latency_ms = (time.perf_counter() - t_start) * 1000
        logger.info(
            "llm_request_complete | request_id={} | latency_ms={:.2f} | response_len={} | success=true",
            request_id,
            latency_ms,
            len(scene_text),
        )

        # Return the generated scene
        return JSONResponse(content={
            "success": True,
            "prompt": request.prompt,
            "include_dice_rolls": request.include_dice_rolls,
            "scene": scene_text,
        })
    except Exception as e:
        latency_ms = (time.perf_counter() - t_start) * 1000
        logger.error(
            "llm_request_failed | request_id={} | latency_ms={:.2f} | error={}",
            request_id,
            latency_ms,
            str(e),
        )
        raise HTTPException(
            status_code=500,
            detail=f"Error generating scene: {str(e)}",
        )
