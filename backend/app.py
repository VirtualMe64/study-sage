#!/usr/bin/env python3
"""
FastAPI backend server for Study Sage
Exposes Python Manim generation capabilities to React frontend
"""

import os
import sys
import json
import asyncio
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

from fastapi import FastAPI, HTTPException, BackgroundTasks, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn

# Add the py_par directory to the Python path
sys.path.append(str(Path(__file__).parent.parent / "py_par"))

# Import the main generation functions
from main import (
    generate_scene_prompt,
    call_openai_api,
    process_scenes_phase2,
    process_scenes_phase3,
    render_videos,
    combine_videos,
    save_scene_map
)

app = FastAPI(
    title="Study Sage API",
    description="Python backend for generating educational Manim animations",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for request/response
class LessonRequest(BaseModel):
    topic: str
    complexity: str = "intermediate"
    depth: str = "detailed"
    style: str = "clean and modern"

class Phase2Request(BaseModel):
    scene_data: Dict[str, Any]

class Phase3Request(BaseModel):
    scene_data: Dict[str, Any]

class RenderRequest(BaseModel):
    phase3_data: Dict[str, Any]

# Global variables for tracking jobs
active_jobs: Dict[str, Dict[str, Any]] = {}

# Create output directories
OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(exist_ok=True)
STATIC_DIR = OUTPUT_DIR / "static"
STATIC_DIR.mkdir(exist_ok=True)

# Mount static files
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Study Sage Python Backend API", "status": "running"}

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

@app.post("/api/lessons/generate")
async def generate_lesson(request: LessonRequest, background_tasks: BackgroundTasks):
    """
    Generate a complete lesson with all phases
    """
    job_id = f"lesson_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    try:
        # Initialize job tracking
        active_jobs[job_id] = {
            "status": "processing",
            "phase": "phase1",
            "progress": 0,
            "result": None,
            "error": None
        }
        
        # Start background processing
        background_tasks.add_task(process_lesson_background, job_id, request)
        
        return {
            "success": True,
            "job_id": job_id,
            "message": "Lesson generation started",
            "status_url": f"/api/jobs/{job_id}"
        }
        
    except Exception as e:
        active_jobs[job_id] = {
            "status": "error",
            "phase": "phase1",
            "progress": 0,
            "result": None,
            "error": str(e)
        }
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/lessons/phase1")
async def generate_phase1(request: LessonRequest):
    """
    Generate Phase 1: Basic scene mapping
    """
    try:
        # Get OpenAI API key
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise HTTPException(status_code=500, detail="OpenAI API key not configured")
        
        # Generate prompt
        prompt = generate_scene_prompt(request.topic)
        
        # Call OpenAI API
        response = call_openai_api(prompt, api_key)
        
        # Parse JSON response
        try:
            scene_data = json.loads(response)
        except json.JSONDecodeError as e:
            raise HTTPException(status_code=500, detail=f"Failed to parse OpenAI response: {e}")
        
        # Add metadata
        scene_data["phase"] = 1
        scene_data["generated_at"] = datetime.now().isoformat()
        scene_data["request"] = request.dict()
        
        return {
            "success": True,
            "data": scene_data,
            "message": "Phase 1 completed successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/lessons/phase2")
async def generate_phase2(request: Phase2Request):
    """
    Generate Phase 2: Detailed script generation
    """
    try:
        # Get OpenAI API key
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise HTTPException(status_code=500, detail="OpenAI API key not configured")
        
        # Process Phase 2
        phase2_data = process_scenes_phase2(request.scene_data, api_key)
        
        return {
            "success": True,
            "data": phase2_data,
            "message": "Phase 2 completed successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/lessons/phase3")
async def generate_phase3(request: Phase3Request):
    """
    Generate Phase 3: Manim code generation
    """
    try:
        # Get OpenAI API key
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise HTTPException(status_code=500, detail="OpenAI API key not configured")
        
        # Process Phase 3
        phase3_data = process_scenes_phase3(request.scene_data, api_key)
        
        return {
            "success": True,
            "data": phase3_data,
            "message": "Phase 3 completed successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/lessons/render")
async def render_lesson_videos(request: RenderRequest, background_tasks: BackgroundTasks):
    """
    Render videos for the lesson
    """
    job_id = f"render_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    try:
        # Initialize job tracking
        active_jobs[job_id] = {
            "status": "processing",
            "phase": "rendering",
            "progress": 0,
            "result": None,
            "error": None
        }
        
        # Start background processing
        background_tasks.add_task(render_videos_background, job_id, request.phase3_data)
        
        return {
            "success": True,
            "job_id": job_id,
            "message": "Video rendering started",
            "status_url": f"/api/jobs/{job_id}"
        }
        
    except Exception as e:
        active_jobs[job_id] = {
            "status": "error",
            "phase": "rendering",
            "progress": 0,
            "result": None,
            "error": str(e)
        }
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/jobs/{job_id}")
async def get_job_status(job_id: str):
    """
    Get the status of a background job
    """
    if job_id not in active_jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return active_jobs[job_id]

@app.get("/api/files/{filename}")
async def download_file(filename: str):
    """
    Download generated files
    """
    file_path = OUTPUT_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(
        path=str(file_path),
        filename=filename,
        media_type='application/octet-stream'
    )

@app.get("/api/files")
async def list_files():
    """
    List all generated files
    """
    files = []
    for file_path in OUTPUT_DIR.rglob("*"):
        if file_path.is_file():
            files.append({
                "name": file_path.name,
                "path": str(file_path.relative_to(OUTPUT_DIR)),
                "size": file_path.stat().st_size,
                "modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
            })
    
    return {"files": files}

# Background task functions
async def process_lesson_background(job_id: str, request: LessonRequest):
    """
    Background task to process a complete lesson
    """
    try:
        # Get OpenAI API key
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise Exception("OpenAI API key not configured")
        
        # Phase 1: Basic scene mapping
        active_jobs[job_id]["phase"] = "phase1"
        active_jobs[job_id]["progress"] = 10
        
        prompt = generate_scene_prompt(request.topic)
        response = call_openai_api(prompt, api_key)
        scene_data = json.loads(response)
        scene_data["phase"] = 1
        
        # Phase 2: Detailed scripts
        active_jobs[job_id]["phase"] = "phase2"
        active_jobs[job_id]["progress"] = 40
        
        phase2_data = process_scenes_phase2(scene_data, api_key)
        
        # Phase 3: Manim code generation
        active_jobs[job_id]["phase"] = "phase3"
        active_jobs[job_id]["progress"] = 70
        
        phase3_data = process_scenes_phase3(phase2_data, api_key)
        
        # Save results
        output_file = OUTPUT_DIR / f"lesson_{job_id}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(phase3_data, f, indent=2, ensure_ascii=False)
        
        # Complete
        active_jobs[job_id]["status"] = "completed"
        active_jobs[job_id]["progress"] = 100
        active_jobs[job_id]["result"] = {
            "phase3_data": phase3_data,
            "output_file": str(output_file.relative_to(OUTPUT_DIR))
        }
        
    except Exception as e:
        active_jobs[job_id]["status"] = "error"
        active_jobs[job_id]["error"] = str(e)

async def render_videos_background(job_id: str, phase3_data: Dict[str, Any]):
    """
    Background task to render videos
    """
    try:
        active_jobs[job_id]["progress"] = 20
        
        # Render videos
        videos = render_videos(phase3_data, str(OUTPUT_DIR))
        
        active_jobs[job_id]["progress"] = 80
        
        # Combine videos
        complete_video = combine_videos(videos, str(OUTPUT_DIR))
        
        active_jobs[job_id]["status"] = "completed"
        active_jobs[job_id]["progress"] = 100
        active_jobs[job_id]["result"] = {
            "videos": videos,
            "complete_video": complete_video,
            "video_count": len(videos)
        }
        
    except Exception as e:
        active_jobs[job_id]["status"] = "error"
        active_jobs[job_id]["error"] = str(e)

if __name__ == "__main__":
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Run the server
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
