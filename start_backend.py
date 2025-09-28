#!/usr/bin/env python3
"""
Simple startup script for Study Sage Flask backend
"""

import os
import sys
from pathlib import Path

# Add the py_par directory to the Python path
current_dir = Path(__file__).parent
py_par_dir = current_dir / "py_par"
sys.path.insert(0, str(py_par_dir))

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

# Import and run the Flask app
from backend.flask_app import app

if __name__ == "__main__":
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
