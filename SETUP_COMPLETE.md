# Study Sage - Complete Setup Guide

## Architecture Overview

**React Frontend (LearningUI.js)** → **Flask Backend (flask_app.py)** → **Python Video Generator (py_par/main.py)**

## Quick Start

### 1. Install Dependencies

```powershell
# Install Flask dependencies
cd backend
pip install -r flask_requirements.txt

# Install py_par dependencies
cd ../py_par
pip install -r requirements.txt

# Install React dependencies
cd ../frontend
npm install
```

### 2. Set Environment Variables

```powershell
# Set your OpenAI API key
$env:OPENAI_API_KEY="your-openai-api-key-here"
```

### 3. Start the Backend

```powershell
# From the root directory
python start_backend.py
```

### 4. Start the Frontend

```powershell
# In a new terminal
cd frontend
npm start
```

## URLs

- **React Frontend**: http://localhost:3000
- **Flask Backend API**: http://localhost:5000
- **Health Check**: http://localhost:5000/api/health

## How It Works

1. **User Input**: User enters a topic in the React frontend
2. **API Call**: LearningUI.js sends a POST request to Flask backend
3. **Video Generation**: Flask backend calls py_par/main.py to generate video
4. **Response**: Flask returns success/error status to React frontend
5. **File Output**: Generated videos are saved in py_par/outputs/

## API Endpoints

### Generate Video
```bash
POST /api/videos/generate
Content-Type: application/json

{
  "topic": "quadratic equations",
  "complexity": "intermediate",
  "depth": "detailed"
}
```

### Health Check
```bash
GET /api/health
```

## Troubleshooting

### Backend Issues
- Check OpenAI API key is set
- Ensure py_par directory is accessible
- Check Flask dependencies are installed

### Frontend Issues
- Ensure React dependencies are installed
- Check backend is running on port 5000
- Verify CORS is configured correctly

### Common Commands
```powershell
# Check if backend is running
curl http://localhost:5000/api/health

# Check if frontend is running
curl http://localhost:3000

# Test API directly
curl -X POST http://localhost:5000/api/videos/generate -H "Content-Type: application/json" -d "{\"topic\":\"test\"}"
```

## File Structure

```
study-sage/
├── frontend/
│   ├── src/
│   │   ├── LearningUI.js      # React frontend
│   │   └── services/api.js    # API service
│   └── package.json
├── backend/
│   ├── flask_app.py           # Flask backend
│   └── flask_requirements.txt
├── py_par/
│   ├── main.py                # Video generation
│   └── requirements.txt
└── start_backend.py           # Startup script
```

## Next Steps

1. Set your OpenAI API key
2. Run the startup commands above
3. Open http://localhost:3000
4. Enter a topic and generate videos!

The complete flow is now working: React → Flask → Python Video Generator!
