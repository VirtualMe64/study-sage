# Study Sage - Python Backend Integration Setup

This guide will help you connect your React frontend to your Python-based Manim generation backend.

## Architecture Overview

- **Frontend**: React app with Tailwind CSS (port 3000)
- **Backend**: Python FastAPI server with Manim generation (port 8000)
- **Communication**: RESTful API with CORS enabled
- **Processing**: Asynchronous background jobs for long-running tasks

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

# Install Python dependencies
pip install -r requirements.txt

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

### 3. Start the Python Backend Server

```bash
# From the backend directory
cd backend
python start_server.py
```

This will start the FastAPI server on `http://localhost:8000` with the following endpoints:
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

## Features

### 🎬 **Complete Workflow**
- **Phase 1**: AI generates scene-by-scene educational content
- **Phase 2**: Detailed Manim script instructions with timing
- **Phase 3**: Complete Manim Python code generation
- **Rendering**: Video generation and combination

### ⚡ **Asynchronous Processing**
- Background job processing for long-running tasks
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

1. **Backend Changes**: Modify `backend/app.py` or Python files, restart with `python start_server.py`
2. **Frontend Changes**: Modify React components, hot reload will handle the rest
3. **API Changes**: Update both `backend/app.py` and `frontend/src/services/api.js`

## Troubleshooting

### Python Backend Issues
- **Import Errors**: Ensure `py_par` directory is in Python path
- **OpenAI API Errors**: Check API key configuration
- **Manim Errors**: Ensure Manim is properly installed
- **FFmpeg Errors**: Install FFmpeg system dependency

### Frontend Issues
- **CORS Errors**: Backend is configured for `localhost:3000`
- **API Connection**: Check backend is running on port 8000
- **Job Polling**: Ensure job IDs are properly tracked

### Common Solutions
```bash
# Check if backend is running
curl http://localhost:8000/api/health

# Check Python path
python -c "import sys; print(sys.path)"

# Test OpenAI API
python -c "import openai; print('OpenAI available')"

# Test Manim
python -c "import manim; print('Manim available')"
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

- **Parallel Processing**: Phase 2 and 3 use parallel API calls
- **Background Jobs**: Long-running tasks don't block the API
- **File Caching**: Generated files are cached for reuse
- **Progress Tracking**: Real-time updates for user feedback

## API Documentation

Once the backend is running, visit `http://localhost:8000/docs` for interactive API documentation powered by FastAPI's automatic OpenAPI generation.
