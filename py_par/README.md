# Python Manim Explainer Scene Generator

This is a Python version of the Manim Explainer Workflow that generates scene-by-scene scripts for educational animations using OpenAI's API.

## Features

- Takes user input for any topic (e.g., Pythagoras, BFS, DP, etc.)
- **Phase 1**: Generates comprehensive scene-by-scene scripts using OpenAI API
- **Phase 2**: Expands each scene with detailed Manim script instructions (parallel processing)
- **Phase 3**: Generates Manim-compatible Python code and renders videos (parallel processing)
- Creates structured JSON output with overview and detailed scenes
- Saves Phase 1 output to `outputs/scene_map_phase_1.json`
- Saves Phase 2 output to `outputs/scene_map_phase_2.json`
- Saves Phase 3 output to `outputs/scene_map_phase_3_results.json`
- Renders individual scene videos in `outputs/mp4s/`
- Creates complete stitched video as `outputs/complete.mp4`
- Displays formatted scene maps in terminal

## Setup

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Set your OpenAI API key (choose one method):

**Option A: Using .env file (recommended)**

```bash
# Copy the example file
cp env.example .env

# Edit .env and add your API key
nano .env
```

**Option B: Using environment variable**

```bash
export OPENAI_API_KEY="your-api-key-here"
```

You can get an API key from: https://platform.openai.com/api-keys

## Usage

### Basic Usage

Run the main script:

```bash
python main.py
```

Enter your topic when prompted, and the script will:

### Command Line Options

```bash
# Basic usage with interactive prompts
python main.py

# Skip all confirmation prompts (auto-proceed through all phases)
python main.py -y

# Specify topic from command line
python main.py --topic "Binary Search Algorithm"

# Combine both options for fully automated processing
python main.py -y --topic "Dynamic Programming"

# Use a different OpenAI model
python main.py --model "gpt-3.5-turbo" --topic "Binary Search"

# Use GPT-4 with automated processing
python main.py -y --model "gpt-4" --topic "Machine Learning"
```

**Command Line Arguments:**

- `-y, --yes`: Skip all confirmation prompts and proceed automatically through all phases
- `--topic TOPIC`: Specify the topic to explain directly from command line
- `--model MODEL`: OpenAI model to use (default: gpt-4o)
- `-h, --help`: Show help message and exit

### Processing Phases

**Phase 1:**

1. Generate a comprehensive scene-by-scene script using OpenAI API
2. Save the JSON output to `outputs/scene_map_phase_1.json`
3. Display the formatted scene map in the terminal

**Phase 2 (Optional):** 4. Ask if you want to proceed to Phase 2 5. If yes, expand each scene with detailed Manim script instructions 6. Save the expanded output to `outputs/scene_map_phase_2.json` 7. Display detailed script information and processing summary

**Phase 3 (Optional):** 8. Ask if you want to proceed to Phase 3 9. If yes, generate Manim-compatible Python code for each scene 10. Save the code output to `outputs/scene_map_phase_3_results.json` 11. Ask if you want to render videos 12. If yes, render individual scene videos and create complete stitched video

## Output Format

### Phase 1 Output (`scene_map_phase_1.json`):

- **Overview**: Title, description, learning objectives, target duration, and format
- **Scenes**: Array of scene objects with:
    - Scene number and title
    - Detailed description
    - Visual elements
    - Key points
    - Manim concepts to use
    - Explanation of why the concept works

### Phase 2 Output (`scene_map_phase_2.json`):

- **All Phase 1 content** plus:
- **Expanded scenes** with additional fields:
    - `expanded_description`: Much more detailed scene description
    - `script`: Detailed Manim script instructions including:
        - `setup`: Object creation and positioning instructions
        - `animations`: Step-by-step animation sequence with timing
        - `cleanup`: Scene transition instructions
        - `total_estimated_time`: Scene duration estimate
        - `manim_objects`: Categorized list of all Manim objects
        - `positioning_guide`: Layout and positioning details
        - `color_scheme`: Color palette for the scene

### Phase 3 Output (`scene_map_phase_3_results.json`):

- **All Phase 1 and Phase 2 content** plus:
- **Manim-compatible format** matching `rendering/result.json`:
    - `lessonPlan`: Title and objectives
    - `sceneFiles`: Array of scene files with:
        - `id`: Scene identifier
        - `className`: Python class name
        - `filename`: Python filename
        - `code`: Complete Manim Python code
        - `validationResults`: Code validation results
    - `masterFile`: Master animation file
    - `totalScenes`: Number of scenes

### Video Outputs:

- **Individual Scene Videos**: `outputs/mp4s/scene_1.mp4`, `scene_2.mp4`, etc.
- **Complete Stitched Video**: `outputs/complete.mp4`
- **Generated Python Files**: `outputs/generated/` directory

## Requirements

- **Python 3.7+**
- **OpenAI API Key**
- **Manim**: For video rendering (`pip install manim`)
- **FFmpeg**: For video combining (system dependency)
- **aiohttp**: For parallel API processing (`pip install aiohttp`)
- **tqdm**: For progress bars (`pip install tqdm`)

## Performance

- **Parallel Processing**: Phase 2 and Phase 3 use parallel API calls for significantly faster processing
- **Concurrent Scenes**: All scenes are processed simultaneously rather than sequentially
- **Faster Generation**: Reduces total processing time by 3-5x depending on the number of scenes
- **Progress Tracking**: Real-time progress bars show processing status for all phases

## User Experience

- **Visual Progress**: Clear progress bars show exactly what's being processed
- **Real-time Updates**: See scenes being processed in real-time during parallel operations
- **Status Indicators**: Clear success/error indicators for each processing step
- **Time Estimates**: Progress bars show estimated completion times

## Example

```bash
$ python main.py
🎬 Manim Explainer Scene Generator
==================================================
Enter the topic you want to create an animation about (e.g., Pythagoras, BFS, DP): Pythagoras

🤖 Generating scene map for: Pythagoras
This may take a moment...
✅ Scene map saved to: ..../outputs/scene_map_phase_1.json

================================================================================
🎬 GENERATED SCENE MAP
================================================================================

📋 OVERVIEW
Title: Pythagorean Theorem: A Visual Journey
Description: An educational animation explaining the Pythagorean theorem through visual demonstrations
Target Duration: 5 minutes
Format: Step-by-step visual proof with interactive elements

🎯 Learning Objectives:
  1. Understand the relationship between sides of a right triangle
  2. Visualize the geometric proof of a² + b² = c²
  3. Apply the theorem to solve practical problems

🎭 SCENES (4 total)
--------------------------------------------------------------------------------

Scene 1: Introduction to Right Triangles
Description: Introduction to right triangles and their properties
...
```

## Scene Structure

Each generated animation follows a structured format:

- **Scene 1**: Introduction to the topic
- **Scene 2**: Table of Contents (overview of what will be covered)
- **Scenes 3-5**: Main educational content (core concepts and explanations)
- **Final Scene**: Thank You/Conclusion (summary and closing)

This ensures a professional presentation with clear navigation and proper conclusion.

## Based On

This Python implementation is based on the TypeScript/Node.js workflow in `src/mastra/` and uses the same prompt framework from `process-scenes-step.ts`.
