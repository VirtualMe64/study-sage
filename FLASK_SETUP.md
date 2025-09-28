# Study Sage - Flask Backend Integration Setup

This guide will help you connect your React frontend to your Python Flask backend with Manim generation capabilities.

## Architecture Overview

- **Frontend**: React app with Tailwind CSS (port 3000)
- **Backend**: Python Flask server with Manim generation (port 5000)
- **Communication**: RESTful API with CORS enabled
- **Processing**: Threading-based background jobs for long-running tasks

## Prerequisites

- Python 3.7+
- Node.js 16+
- OpenAI API Key
- FFmpeg (for video processing)

## Setup Instructions

### 1. Install Python Backend Dependencies

```bash
# Navigate to backend directory
cd backend

# Install Flask dependencies
pip install -r flask_requirements.txt

# Install additional dependencies from py_par
cd ../py_par
pip install -r requirements.txt
```

### 2. Set Up Environment Variables

Create a `.env` file in the root directory:

```bash
# In the root directory (study-sage/)
echo "OPENAI_API_KEY=your-openai-api-key-here" > .env
```

Or set the environment variable directly:

```bash
export OPENAI_API_KEY="your-openai-api-key-here"
```

### 3. Start the Flask Backend Server

```bash
# From the backend directory
cd backend
python start_flask.py
```

This will start the Flask server on `http://localhost:5000` with the following endpoints:
- `GET /api/health` - Health check
- `POST /api/lessons/generate` - Generate complete lesson (all phases)
- `POST /api/lessons/phase1` - Generate Phase 1 only (scene mapping)
- `POST /api/lessons/phase2` - Generate Phase 2 only (detailed scripts)
- `POST /api/lessons/phase3` - Generate Phase 3 only (Manim code)
- `POST /api/lessons/render` - Render videos
- `GET /api/jobs/{job_id}` - Check job status
- `GET /api/files` - List generated files
- `GET /api/files/{filename}` - Download files

### 4. Start the Frontend Development Server

```bash
# In a new terminal, navigate to frontend directory
cd frontend

# Install dependencies (if not already done)
npm install

# Start the React development server
npm start
```

This will start the React app on `http://localhost:3000`

### 5. Test the Integration

1. Open `http://localhost:3000` in your browser
2. Enter a topic (e.g., "quadratic equations")
3. Select complexity and depth
4. Click "Generate"
5. Watch as the AI generates educational content in phases!

## API Endpoints

### Complete Lesson Generation
```bash
POST /api/lessons/generate
Content-Type: application/json

{
  "topic": "quadratic equations",
  "complexity": "intermediate",
  "depth": "detailed",
  "style": "clean and modern"
}
```

### Phase-by-Phase Generation
```bash
# Phase 1: Scene Mapping
POST /api/lessons/phase1
{
  "topic": "quadratic equations",
  "complexity": "intermediate",
  "depth": "detailed",
  "style": "clean and modern"
}

# Phase 2: Detailed Scripts
POST /api/lessons/phase2
{
  "scene_data": { /* Phase 1 result */ }
}

# Phase 3: Manim Code
POST /api/lessons/phase3
{
  "scene_data": { /* Phase 2 result */ }
}

# Video Rendering
POST /api/lessons/render
{
  "phase3_data": { /* Phase 3 result */ }
}
```

### Job Status Checking
```bash
GET /api/jobs/{job_id}
```

### File Management
```bash
# List all generated files
GET /api/files

# Download a specific file
GET /api/files/{filename}
```

## Flask vs FastAPI Comparison

### ✅ **Flask Advantages**
- **Simpler**: Easier to understand and debug
- **Lightweight**: Minimal dependencies
- **Familiar**: More developers know Flask
- **Flexible**: Easy to customize and extend
- **Debug Mode**: Built-in debugger and auto-reload

### ⚡ **FastAPI Advantages**
- **Performance**: Faster request handling
- **Type Safety**: Built-in Pydantic validation
- **Auto Documentation**: Automatic OpenAPI/Swagger docs
- **Async Support**: Native async/await support
- **Modern**: More modern Python features

### 🎯 **For Your Use Case**
Flask is perfect because:
- Simpler setup and debugging
- Your processing is CPU-bound (not I/O-bound)
- You don't need complex async patterns
- Easier to understand and maintain
- Great for educational projects

## Features

### 🎬 **Complete Workflow**
- **Phase 1**: AI generates scene-by-scene educational content
- **Phase 2**: Detailed Manim script instructions with timing
- **Phase 3**: Complete Manim Python code generation
- **Rendering**: Video generation and combination

### ⚡ **Background Processing**
- Threading-based background jobs
- Real-time progress tracking
- Job status polling
- Error handling and recovery

### 📁 **File Management**
- Automatic file generation and storage
- File listing and download endpoints
- Static file serving for generated content

### 🔄 **Step-by-Step Generation**
- Generate individual phases
- Chain phases together
- Resume from any phase
- Flexible workflow control

## Development Workflow

1. **Backend Changes**: Modify `backend/flask_app.py`, restart with `python start_flask.py`
2. **Frontend Changes**: Modify React components, hot reload will handle the rest
3. **API Changes**: Update both `backend/flask_app.py` and `frontend/src/services/api.js`

## Troubleshooting

### Flask Backend Issues
- **Import Errors**: Ensure `py_par` directory is in Python path
- **OpenAI API Errors**: Check API key configuration
- **Manim Errors**: Ensure Manim is properly installed
- **FFmpeg Errors**: Install FFmpeg system dependency
- **Threading Issues**: Check if background jobs are completing

### Frontend Issues
- **CORS Errors**: Flask is configured for `localhost:3000`
- **API Connection**: Check backend is running on port 5000
- **Job Polling**: Ensure job IDs are properly tracked

### Common Solutions
```bash
# Check if backend is running
curl http://localhost:5000/api/health

# Check Python path
python -c "import sys; print(sys.path)"

# Test OpenAI API
python -c "import openai; print('OpenAI available')"

# Test Manim
python -c "import manim; print('Manim available')"

# Check Flask installation
python -c "import flask; print('Flask available')"
```

## Production Deployment

For production deployment:

1. **Backend**: Use Gunicorn or similar WSGI server
2. **Frontend**: Build with `npm run build` and serve static files
3. **Environment**: Set production environment variables
4. **Database**: Add persistent storage for job tracking
5. **File Storage**: Use cloud storage for generated files
6. **Monitoring**: Add logging and error tracking

## Performance Notes

- **Threading**: Background jobs use Python threading
- **File Caching**: Generated files are cached for reuse
- **Progress Tracking**: Real-time updates for user feedback
- **Memory Usage**: Threading uses more memory than async

## Quick Start Commands

```bash
# Install dependencies
cd backend && pip install -r flask_requirements.txt
cd ../py_par && pip install -r requirements.txt

# Set API key
export OPENAI_API_KEY="your-api-key-here"

# Start backend
cd backend && python start_flask.py

# Start frontend (in new terminal)
cd frontend && npm start
```

## Why Flask is Great for This Project

1. **Simplicity**: Easy to understand and debug
2. **Flexibility**: Easy to add new endpoints
3. **Community**: Large community and resources
4. **Learning**: Great for educational purposes
5. **Debugging**: Built-in debugger and error pages
6. **Lightweight**: Fast startup and low memory usage

The Flask backend provides all the same functionality as FastAPI but with a simpler, more approachable codebase that's perfect for your Study Sage project!
