#!/usr/bin/env python3
"""
Flask backend server for Study Sage
Exposes Python Manim generation capabilities to React frontend
"""

import os
import sys
import json
import threading
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS

# Add the py_par directory to the Python path
sys.path.append(str(Path(__file__).parent.parent / "py_par"))

# Import the main generation functions from py_par
from main import (
    generate_scene_prompt,
    call_openai_api,
    process_scenes_phase2,
    process_scenes_phase3,
    render_videos,
    combine_videos,
    save_scene_map
)

app = Flask(__name__)
CORS(app, origins=["http://localhost:3000", "http://127.0.0.1:3000"])

# Global variables for tracking jobs
active_jobs: Dict[str, Dict[str, Any]] = {}

# Create output directories
OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(exist_ok=True)

@app.route("/")
def root():
    """Root endpoint"""
    return jsonify({
        "message": "Study Sage Python Backend API", 
        "status": "running",
        "version": "1.0.0"
    })

@app.route("/api/health", methods=["GET"])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    })

@app.route("/api/lessons/generate", methods=["POST"])
def generate_lesson():
    """
    Generate a complete lesson with all phases using py_par/main.py
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        topic = data.get("topic")
        if not topic:
            return jsonify({"error": "Topic is required"}), 400
        
        complexity = data.get("complexity", "intermediate")
        depth = data.get("depth", "detailed")
        style = data.get("style", "clean and modern")
        
        job_id = f"lesson_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Initialize job tracking
        active_jobs[job_id] = {
            "status": "processing",
            "phase": "phase1",
            "progress": 0,
            "result": None,
            "error": None
        }
        
        # Start background processing
        thread = threading.Thread(
            target=process_lesson_background,
            args=(job_id, topic, complexity, depth, style)
        )
        thread.daemon = True
        thread.start()
        
        return jsonify({
            "success": True,
            "job_id": job_id,
            "message": "Lesson generation started",
            "status_url": f"/api/jobs/{job_id}"
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/lessons/phase1", methods=["POST"])
def generate_phase1():
    """
    Generate Phase 1: Basic scene mapping
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        topic = data.get("topic")
        if not topic:
            return jsonify({"error": "Topic is required"}), 400
        
        complexity = data.get("complexity", "intermediate")
        depth = data.get("depth", "detailed")
        style = data.get("style", "clean and modern")
        
        # Get OpenAI API key
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            return jsonify({"error": "OpenAI API key not configured"}), 500
        
        # Generate prompt
        prompt = generate_scene_prompt(topic)
        
        # Call OpenAI API
        response = call_openai_api(prompt, api_key)
        
        # Parse JSON response
        try:
            scene_data = json.loads(response)
        except json.JSONDecodeError as e:
            return jsonify({"error": f"Failed to parse OpenAI response: {e}"}), 500
        
        # Add metadata
        scene_data["phase"] = 1
        scene_data["generated_at"] = datetime.now().isoformat()
        scene_data["request"] = {
            "topic": topic,
            "complexity": complexity,
            "depth": depth,
            "style": style
        }
        
        return jsonify({
            "success": True,
            "data": scene_data,
            "message": "Phase 1 completed successfully"
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/videos/generate", methods=["POST"])
def generate_video():
    """
    Generate video using py_par/main.py directly
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        topic = data.get("topic")
        if not topic:
            return jsonify({"error": "Topic is required"}), 400
        
        complexity = data.get("complexity", "intermediate")
        depth = data.get("depth", "detailed")
        
        # Get OpenAI API key
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            return jsonify({"error": "OpenAI API key not configured"}), 500
        
        # Call the main function from py_par/main.py
        try:
            # Import and call the main function
            from main import main_main as generate_video_main
            
            # Set up arguments for the main function
            import argparse
            args = argparse.Namespace()
            args.topic = topic
            args.complexity = complexity
            args.depth = depth
            args.yes = True  # Skip confirmations
            args.model = "gpt-4o"  # Default model
            
            # Call the main function
            result = generate_video_main(args)
            
            return jsonify({
                "success": True,
                "message": "Video generation completed",
                "topic": topic,
                "complexity": complexity,
                "depth": depth
            })
            
        except Exception as e:
            return jsonify({"error": f"Video generation failed: {str(e)}"}), 500
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/jobs/<job_id>", methods=["GET"])
def get_job_status(job_id):
    """
    Get the status of a background job
    """
    if job_id not in active_jobs:
        return jsonify({"error": "Job not found"}), 404
    
    return jsonify(active_jobs[job_id])

# Background task functions
def process_lesson_background(job_id: str, topic: str, complexity: str, depth: str, style: str):
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
        
        prompt = generate_scene_prompt(topic)
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

if __name__ == "__main__":
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Check for required environment variables
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ Error: OPENAI_API_KEY environment variable not set")
        print("Please set your OpenAI API key:")
        print("  export OPENAI_API_KEY='your-api-key-here'")
        print("Or create a .env file with: OPENAI_API_KEY=your-api-key-here")
        sys.exit(1)
    
    print("🚀 Starting Study Sage Flask Backend...")
    print("📡 API will be available at: http://localhost:5000")
    print("📚 API endpoints available at: http://localhost:5000/api")
    print("🔧 Debug mode enabled")
    
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True,
        threaded=True
    )
