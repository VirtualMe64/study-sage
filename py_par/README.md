# Python Manim Explainer Scene Generator

This is a Python version of the Manim Explainer Workflow that generates scene-by-scene scripts for educational animations using OpenAI's API.

## Features

- Takes user input for any topic (e.g., Pythagoras, BFS, DP, etc.)
- **Phase 1**: Generates comprehensive scene-by-scene scripts using OpenAI API
- **Phase 2**: Expands each scene with detailed Manim script instructions
- Creates structured JSON output with overview and detailed scenes
- Saves Phase 1 output to `outputs/scene_map_phase_1.json`
- Saves Phase 2 output to `outputs/scene_map_phase2.json`
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

Run the main script:

```bash
python main.py
```

Enter your topic when prompted, and the script will:

**Phase 1:**

1. Generate a comprehensive scene-by-scene script using OpenAI API
2. Save the JSON output to `outputs/scene_map_phase_1.json`
3. Display the formatted scene map in the terminal

**Phase 2 (Optional):** 4. Ask if you want to proceed to Phase 2 5. If yes, expand each scene with detailed Manim script instructions 6. Save the expanded output to `outputs/scene_map_phase2.json` 7. Display detailed script information and processing summary

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

### Phase 2 Output (`scene_map_phase2.json`):

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

## Example

```bash
$ python main.py
🎬 Manim Explainer Scene Generator
==================================================
Enter the topic you want to create an animation about (e.g., Pythagoras, BFS, DP): Pythagoras

🤖 Generating scene map for: Pythagoras
This may take a moment...
✅ Scene map saved to: /home/zanger/Documents/cs/m-ai-nim/py_par/outputs/scene_map_phase_1.json

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

## Based On

This Python implementation is based on the TypeScript/Node.js workflow in `src/mastra/` and uses the same prompt framework from `process-scenes-step.ts`.
