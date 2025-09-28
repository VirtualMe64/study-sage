#!/usr/bin/env python3
"""
Python version of the Manim Explainer Workflow
Generates scene-by-scene scripts for educational animations using OpenAI API
"""

import json
import os
import shutil
import subprocess
import asyncio
import aiohttp
import argparse
from openai import OpenAI
from typing import Dict, Any, List
from dotenv import load_dotenv
from tqdm.asyncio import tqdm

# Default OpenAI model to use
DEFAULT_MODEL = "gpt-5-nano"

def get_user_input(prompt: str, skip_confirm: bool = False) -> bool:
    """
    Get user input with optional skip confirmation
    """
    if skip_confirm:
        print(f"{prompt} (auto-proceeding with -y flag)")
        return True
    
    response = input(f"{prompt} (y/n): ").lower().strip()
    return response in ['y', 'yes', '1', 'true']

def generate_scene_prompt(topic: str) -> str:
    """
    Generate the prompt for OpenAI API to create a scene-by-scene script
    Based on the prompt framework from process-scenes-step.ts
    """
    return f"""Create a comprehensive scene-by-scene script for an educational animation about "{topic}".

This animation will be generated using Manim (Mathematical Animation Engine) to create a visual explainer video.

Requirements:
1. Provide an overview of the potential video describing the overall format and goal
2. Create a detailed scene-by-scene description of what should be shown
3. Include specific visual elements that demonstrate how the concept is visualized
4. Explain why the topic works/exists and its significance
5. Each scene should be educational and build upon previous scenes
6. Consider visual storytelling and mathematical animation best practices
7. Duration should be realistic for educational content (3-8 minutes total)
8. MUST include a Table of Contents scene as scene 2 (after the introduction)
9. MUST include a Thank You/Conclusion scene as the final scene

The output should be in VALID JSON FORMAT with the following structure:

{{
    "overview": {{
        "title": "Title of the educational video",
        "description": "Brief description of what the video will teach",
        "learning_objectives": ["Objective 1", "Objective 2", "Objective 3"],
        "target_duration": "Estimated total duration in minutes",
        "format": "Description of the overall video format and approach"
    }},
    "scenes": [
        {{
            "scene_number": 1,
            "title": "Scene Title",
            "description": "Detailed description of what happens in this scene",
            "visual_elements": ["Element 1", "Element 2", "Element 3"],
            "key_points": ["Key point 1", "Key point 2"],
            "manim_concepts": ["Write", "Create", "Transform", "FadeIn", "FadeOut"],
            "explanation": "Why this concept works/exists and its significance"
        }},
        {{
            "scene_number": 2,
            "title": "Scene Title",
            "description": "Detailed description of what happens in this scene",
            "visual_elements": ["Element 1", "Element 2", "Element 3"],
            "key_points": ["Key point 1", "Key point 2"],
            "manim_concepts": ["Write", "Create", "Transform", "FadeIn", "FadeOut"],
            "explanation": "Why this concept works/exists and its significance"
        }}
    ]
}}

Manim concepts you should reference include:
- Text animations: Write, AddTextLetterByLetter, RemoveTextLetterByLetter
- Basic animations: FadeIn, FadeOut, Transform, ReplacementTransform
- Mathematical objects: MathTex, Tex, NumberLine, Axes, Graph
- Geometric shapes: Circle, Rectangle, Polygon, Arrow
- Groups and positioning: VGroup, arrange, next_to, to_edge
- Advanced: Create, DrawBorderThenFill, Succession, AnimationGroup

Generate 4-6 scenes that would create an engaging educational Manim animation about {topic}.
The scenes must include:
- Scene 1: Introduction to the topic
- Scene 2: Table of Contents (overview of what will be covered)
- Scenes 3-5: Main educational content (core concepts and explanations)
- Final Scene: Thank You/Conclusion (summary and closing)

Focus on visual demonstrations and clear explanations of why the concept works.

Return ONLY the JSON response, no additional text or formatting."""

def generate_scene_script_prompt(scene: Dict[str, Any]) -> str:
    """
    Generate a detailed prompt for expanding a single scene with script instructions
    """
    return f"""You are an expert Manim animation director. Expand and detail the following scene for a Manim educational animation.

SCENE TO EXPAND:
- Title: {scene.get('title', 'N/A')}
- Description: {scene.get('description', 'N/A')}
- Visual Elements: {', '.join(scene.get('visual_elements', []))}
- Key Points: {', '.join(scene.get('key_points', []))}
- Manim Concepts: {', '.join(scene.get('manim_concepts', []))}
- Explanation: {scene.get('explanation', 'N/A')}

REQUIREMENTS:
1. Expand the scene description with much more detail
2. Add a "script" field with detailed animation instructions
3. The script should include:
   - Specific Manim objects to create (Text, MathTex, Circle, etc.)
   - Exact positioning data (coordinates, alignment, buff values)
   - Animation sequence and timing (self.play(), self.wait())
   - Color schemes and styling details
   - Transitions between elements
   - Camera movements if needed
   - Specific LaTeX/MathTex content
   - Grouping and arrangement instructions

OUTPUT FORMAT (JSON):
{{
    "expanded_description": "Much more detailed description of what happens in this scene",
    "script": {{
        "setup": [
            "Detailed setup instructions for creating objects",
            "Positioning and styling details",
            "Initial state preparations"
        ],
        "animations": [
            {{
                "step": 1,
                "action": "self.play(Write(title), run_time=2)",
                "description": "Write the main title with 2-second duration",
                "objects": ["title"],
                "timing": 2
            }},
            {{
                "step": 2,
                "action": "self.wait(1)",
                "description": "Pause for emphasis",
                "objects": [],
                "timing": 1
            }}
        ],
        "cleanup": [
            "Instructions for transitioning out of the scene",
            "Object removal or transformation details"
        ],
        "total_estimated_time": "Estimated total scene duration in seconds",
        "manim_objects": {{
            "text_objects": ["List of all text objects to create"],
            "math_objects": ["List of all mathematical objects"],
            "geometric_objects": ["List of all shapes and geometric elements"],
            "groups": ["List of VGroup arrangements"]
        }},
        "positioning_guide": {{
            "center": "Main content positioning",
            "left_side": "Left side elements",
            "right_side": "Right side elements",
            "top": "Header/title positioning",
            "bottom": "Footer elements"
        }},
        "color_scheme": {{
            "primary": "Main color for key elements",
            "secondary": "Supporting color",
            "accent": "Highlight color",
            "background": "Background color"
        }}
    }}
}}

Be extremely detailed and specific. Include exact Manim code snippets, precise positioning, and comprehensive animation sequences. The script should be ready for a Manim developer to implement directly.

Return ONLY the JSON response, no additional text."""

def call_openai_api(prompt: str, api_key: str, model: str = DEFAULT_MODEL) -> str:
    """
    Call OpenAI API with the given prompt
    """
    try:
        client = OpenAI(api_key=api_key)
        
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert educational content creator specializing in Manim (Mathematical Animation Engine) animations. You create comprehensive scene-by-scene scripts for educational videos that will be animated using Manim. Always respond with valid JSON format as requested."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            # temperature=0.7,
            # max_tokens=4000
        )
        
        return response.choices[0].message.content.strip()
    
    except Exception as e:
        print(f"Error calling OpenAI API: {e}")
        raise

async def call_openai_api_async(session: aiohttp.ClientSession, prompt: str, api_key: str, model: str = DEFAULT_MODEL) -> str:
    """
    Async call to OpenAI API with the given prompt
    """
    try:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are an expert educational content creator specializing in Manim (Mathematical Animation Engine) animations. You create comprehensive scene-by-scene scripts for educational videos that will be animated using Manim. Always respond with valid JSON format as requested."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            # "temperature": 0.7,
            # "max_tokens": 4000
        }
        
        async with session.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=data
        ) as response:
            if response.status == 200:
                result = await response.json()
                return result["choices"][0]["message"]["content"].strip()
            else:
                error_text = await response.text()
                raise aiohttp.ClientResponseError(
                    request_info=response.request_info,
                    history=response.history,
                    status=response.status,
                    message=f"OpenAI API error {response.status}: {error_text}"
                )
    
    except Exception as e:
        print(f"Error calling OpenAI API: {e}")
        raise

def save_scene_map(scene_data: Dict[str, Any], output_path: str) -> None:
    """
    Save the scene map to a JSON file
    """
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(scene_data, f, indent=2, ensure_ascii=False)
        print("✅ Scene map saved to:", output_path)
    except Exception as e:
        print(f"Error saving scene map: {e}")
        raise

async def process_scene_phase2_async(session: aiohttp.ClientSession, scene: Dict[str, Any], api_key: str, scene_index: int, total_scenes: int, model: str = DEFAULT_MODEL) -> Dict[str, Any]:
    """
    Process a single scene through Phase 2 asynchronously
    """
    print(f"\n📝 Processing scene {scene_index}/{total_scenes}: {scene.get('title', 'N/A')}")
    
    try:
        # Generate detailed prompt for this scene
        prompt = generate_scene_script_prompt(scene)
        
        # Call OpenAI API asynchronously
        response = await call_openai_api_async(session, prompt, api_key, model)
        
        # Parse JSON response
        try:
            expanded_data = json.loads(response)
        except json.JSONDecodeError as e:
            print(f"❌ Error parsing JSON for scene {scene_index}: {e}")
            # Fallback: keep original scene with basic script
            expanded_scene = scene.copy()
            expanded_scene['expanded_description'] = scene.get('description', '')
            expanded_scene['script'] = {
                'setup': ['Error generating detailed script'],
                'animations': [],
                'cleanup': [],
                'total_estimated_time': 0,
                'manim_objects': {},
                'positioning_guide': {},
                'color_scheme': {}
            }
            return expanded_scene
        
        # Merge original scene with expanded data
        expanded_scene = scene.copy()
        expanded_scene['expanded_description'] = expanded_data.get('expanded_description', scene.get('description', ''))
        expanded_scene['script'] = expanded_data.get('script', {})
        
        print(f"✅ Scene {scene_index} expanded successfully")
        return expanded_scene
        
    except (ValueError, KeyError, TypeError) as e:
        print(f"❌ Error processing scene {scene_index}: {e}")
        # Fallback: keep original scene
        expanded_scene = scene.copy()
        expanded_scene['expanded_description'] = scene.get('description', '')
        expanded_scene['script'] = {
            'setup': ['Error generating detailed script'],
            'animations': [],
            'cleanup': [],
            'total_estimated_time': 0,
            'manim_objects': {},
            'positioning_guide': {},
            'color_scheme': {}
        }
        return expanded_scene

async def process_scenes_phase2_async(scene_data: Dict[str, Any], api_key: str, model: str = DEFAULT_MODEL) -> Dict[str, Any]:
    """
    Process all scenes through Phase 2 in parallel to add detailed script instructions
    """
    print("\n🎬 PHASE 2: Expanding scenes with detailed scripts (Parallel Processing)")
    print("="*70)
    
    scenes = scene_data.get('scenes', [])
    
    # Create async session and process all scenes in parallel
    async with aiohttp.ClientSession() as session:
        tasks = []
        for i, scene in enumerate(scenes, 1):
            task = process_scene_phase2_async(session, scene, api_key, i, len(scenes), model)
            tasks.append(task)
        
        # Wait for all tasks to complete with progress bar
        print(f"\n📝 Processing {len(scenes)} scenes in parallel...")
        expanded_scenes = await tqdm.gather(*tasks, desc="Phase 2: Expanding scenes", unit="scene")
        
        # Handle any exceptions that occurred
        processed_scenes = []
        for i, result in enumerate(expanded_scenes, 1):
            if isinstance(result, Exception):
                print(f"❌ Exception in scene {i}: {result}")
                # Create fallback scene
                fallback_scene = scenes[i-1].copy()
                fallback_scene['expanded_description'] = scenes[i-1].get('description', '')
                fallback_scene['script'] = {
                    'setup': ['Error generating detailed script'],
                    'animations': [],
                    'cleanup': [],
                    'total_estimated_time': 0,
                    'manim_objects': {},
                    'positioning_guide': {},
                    'color_scheme': {}
                }
                processed_scenes.append(fallback_scene)
            else:
                processed_scenes.append(result)
    
    # Create Phase 2 output
    phase2_data = scene_data.copy()
    phase2_data['scenes'] = processed_scenes
    phase2_data['phase'] = 2
    phase2_data['processing_notes'] = "Scenes expanded with detailed Manim script instructions (parallel processing)"
    
    return phase2_data

def process_scenes_phase2(scene_data: Dict[str, Any], api_key: str, model: str = DEFAULT_MODEL) -> Dict[str, Any]:
    """
    Wrapper function to run the async Phase 2 processing
    """
    return asyncio.run(process_scenes_phase2_async(scene_data, api_key, model))

def print_scene_map(scene_data: Dict[str, Any]) -> None:
    """
    Print the scene map to terminal in a formatted way
    """
    phase = scene_data.get('phase', 1)
    phase_text = "PHASE 1" if phase == 1 else "PHASE 2"
    
    print("\n" + "="*80)
    print(f"🎬 GENERATED SCENE MAP - {phase_text}")
    print("="*80)
    
    # Print overview
    overview = scene_data.get('overview', {})
    print("\n📋 OVERVIEW")
    print("Title:", overview.get('title', 'N/A'))
    print("Description:", overview.get('description', 'N/A'))
    print("Target Duration:", overview.get('target_duration', 'N/A'))
    print("Format:", overview.get('format', 'N/A'))
    
    print("\n🎯 Learning Objectives:")
    for i, objective in enumerate(overview.get('learning_objectives', []), 1):
        print(f"  {i}. {objective}")
    
    # Print scenes
    scenes = scene_data.get('scenes', [])
    print(f"\n🎭 SCENES ({len(scenes)} total)")
    print("-" * 80)
    
    for scene in scenes:
        print(f"\nScene {scene.get('scene_number', 'N/A')}: {scene.get('title', 'N/A')}")
        
        # Show expanded description if available (Phase 2)
        if 'expanded_description' in scene:
            print(f"Expanded Description: {scene.get('expanded_description', 'N/A')}")
        else:
            print(f"Description: {scene.get('description', 'N/A')}")
        
        print("\nVisual Elements:")
        for element in scene.get('visual_elements', []):
            print(f"  • {element}")
        
        print("\nKey Points:")
        for point in scene.get('key_points', []):
            print(f"  • {point}")
        
        print(f"\nManim Concepts: {', '.join(scene.get('manim_concepts', []))}")
        print("Explanation:", scene.get('explanation', 'N/A'))
        
        # Show script details if available (Phase 2)
        if 'script' in scene and scene['script']:
            script = scene['script']
            print("\n📜 SCRIPT DETAILS:")
            print(f"  Total Estimated Time: {script.get('total_estimated_time', 'N/A')} seconds")
            print(f"  Animation Steps: {len(script.get('animations', []))}")
            print(f"  Setup Instructions: {len(script.get('setup', []))}")
            print(f"  Cleanup Instructions: {len(script.get('cleanup', []))}")
            
            # Show color scheme if available
            color_scheme = script.get('color_scheme', {})
            if color_scheme:
                print(f"  Color Scheme: {color_scheme}")
        
        print("-" * 80)
    
    print("\n" + "="*80)

def print_phase2_summary(scene_data: Dict[str, Any]) -> None:
    """
    Print a summary of Phase 2 processing results
    """
    print("\n" + "="*80)
    print("🎬 PHASE 2 PROCESSING SUMMARY")
    print("="*80)
    
    scenes = scene_data.get('scenes', [])
    total_scenes = len(scenes)
    scenes_with_scripts = sum(1 for scene in scenes if 'script' in scene and scene['script'])
    
    print("\n📊 PROCESSING STATISTICS:")
    print("  Total Scenes:", total_scenes)
    print("  Scenes with Scripts:", scenes_with_scripts)
    print(f"  Success Rate: {(scenes_with_scripts/total_scenes*100):.1f}%" if total_scenes > 0 else "  Success Rate: 0%")
    
    print("\n📝 SCRIPT DETAILS BY SCENE:")
    for i, scene in enumerate(scenes, 1):
        script = scene.get('script', {})
        if script:
            animations = script.get('animations', [])
            setup = script.get('setup', [])
            cleanup = script.get('cleanup', [])
            total_time = script.get('total_estimated_time', 0)
            
            print(f"\n  Scene {i}: {scene.get('title', 'N/A')}")
            print(f"    • Animation Steps: {len(animations)}")
            print(f"    • Setup Instructions: {len(setup)}")
            print(f"    • Cleanup Instructions: {len(cleanup)}")
            print(f"    • Estimated Duration: {total_time} seconds")
        else:
            print(f"\n  Scene {i}: {scene.get('title', 'N/A')} - No script generated")
    
    print("\n" + "="*80)

def generate_manim_code_prompt(overview: Dict[str, Any], scene: Dict[str, Any]) -> str:
    """
    Generate a prompt for creating Manim-compatible Python code for a single scene
    """
    return f"""You are an expert Manim developer. Generate complete, working Manim Python code for an educational animation scene.

OVERVIEW CONTEXT:
- Title: {overview.get('title', 'N/A')}
- Description: {overview.get('description', 'N/A')}
- Learning Objectives: {', '.join(overview.get('learning_objectives', []))}
- Target Duration: {overview.get('target_duration', 'N/A')}
- Format: {overview.get('format', 'N/A')}

SCENE CONTEXT:
- Scene Number: {scene.get('scene_number', 'N/A')}
- Title: {scene.get('title', 'N/A')}
- Description: {scene.get('description', 'N/A')}
- Expanded Description: {scene.get('expanded_description', 'N/A')}
- Visual Elements: {', '.join(scene.get('visual_elements', []))}
- Key Points: {', '.join(scene.get('key_points', []))}
- Manim Concepts: {', '.join(scene.get('manim_concepts', []))}
- Explanation: {scene.get('explanation', 'N/A')}

SCRIPT DETAILS:
{json.dumps(scene.get('script', {}), indent=2) if scene.get('script') else 'No script details available'}

REQUIREMENTS:
1. Create a complete Python class that inherits from Scene
2. Use appropriate Manim objects and animations based on the script details
    - DO NOT use SVGMobject or any external file references (stick_figure, etc.)
    - Use basic shapes like Circle, Rectangle, Polygon, or VGroup for visual elements
    - DO NOT use self.camera.frame (deprecated API) - use self.camera.frame_center or avoid camera animations
    - DO NOT use font_size parameter in get_tex() - use scale() method instead
    - Use only standard fonts: "Arial", "Times New Roman", "Courier New", "Helvetica", "Verdana"
3. Include proper timing with self.play() and self.wait()
4. Make the animation educational and visually clear
5. Use the suggested Manim concepts where appropriate
6. Include descriptive comments explaining the animation logic
7. Ensure the code is syntactically correct and executable
8. Make the class name descriptive (based on the scene title)
9. CRITICAL: Use Create instead of ShowCreation (ShowCreation is deprecated)
10. CRITICAL: Properly escape backslashes in strings - use raw strings (r"") or double backslashes (\\\\) for LaTeX/MathTex
11. CRITICAL: NEVER use multiline strings - keep all MathTex/Tex content on single lines
12. CRITICAL: For complex LaTeX like tables, use string concatenation or variables, NOT multiline strings
13. CRITICAL: For camera animations, use self.camera.frame_center.animate.move_to() instead of self.camera.frame
14. CRITICAL: For brace labels, use brace.get_tex().scale() instead of font_size parameter
15. CRITICAL: Avoid complex camera operations - use simple transforms instead

COMMON MISTAKES TO AVOID:
- self.camera.frame.animate.scale() → Use self.camera.frame_center.animate.move_to() or avoid camera animations
- brace.get_tex(text, font_size=36) → Use brace.get_tex(text).scale(0.8)
- Text(text, font="CMU Serif") → Use Text(text, font="Arial") or no font parameter
- Complex camera movements → Use simple object transformations instead

SAFE ALTERNATIVES:
- Instead of camera animations, use object scaling and movement
- Instead of font_size in get_tex(), use .scale() method
- Instead of custom fonts, use default fonts or specify safe ones
- Instead of complex camera operations, use simple transforms

EXAMPLE OF CORRECT PATTERNS:
```python
from manim import *

class ExampleScene(Scene):
    def construct(self):
        # Correct: Use basic shapes
        circle = Circle(radius=1, color=BLUE)
        
        # Correct: Use .scale() instead of font_size
        brace = BraceBetweenPoints(LEFT, RIGHT, direction=UP)
        label = brace.get_tex("text").scale(0.8)
        
        # Correct: Use standard fonts or no font parameter
        text = Text("Hello", font="Arial")
        
        # Correct: Use Create instead of ShowCreation
        self.play(Create(circle))
        
        # Correct: Avoid camera animations, use object transforms
        self.play(circle.animate.scale(2).move_to(UP))
        
        # Correct: Use VGroup for complex objects
        group = VGroup(circle, text)
        self.play(group.animate.arrange(RIGHT))
```

OUTPUT FORMAT (JSON):
{{
    "className": "DescriptiveClassName",
    "filename": "descriptive_filename.py",
    "code": "Complete Manim Python code here",
    "validationResults": {{
        "syntaxValid": true,
        "manimCompatible": true,
        "warnings": [],
        "suggestions": []
    }}
}}

The animation should effectively teach the concept through visual storytelling and smooth transitions.
Follow the script details closely for positioning, timing, and visual elements.

Return ONLY the JSON response, no additional text."""

def validate_manim_code(code: str) -> Dict[str, Any]:
    """
    Validate Manim code for common issues and problematic patterns
    """
    issues = []
    warnings = []
    
    # Check for deprecated camera API
    if "self.camera.frame" in code:
        issues.append("Uses deprecated camera.frame API - should use camera.frame_center or avoid camera animations")
    
    # Check for font_size parameter in get_tex
    if "font_size=" in code and "get_tex" in code:
        issues.append("Uses font_size parameter in get_tex() - should use .scale() method instead")
    
    # Check for problematic fonts
    problematic_fonts = ["CMU Serif", "CMU Sans", "CMU Typewriter", "Computer Modern"]
    for font in problematic_fonts:
        if font in code:
            warnings.append(f"Uses potentially problematic font '{font}' - consider using standard fonts")
    
    # Check for SVGMobject usage
    if "SVGMobject" in code:
        issues.append("Uses SVGMobject - should use basic shapes instead")
    
    # Check for ShowCreation usage
    if "ShowCreation" in code:
        issues.append("Uses deprecated ShowCreation - should use Create instead")
    
    # Check for multiline strings in MathTex
    if '"""' in code and "MathTex" in code:
        warnings.append("Uses multiline strings with MathTex - may cause issues")
    
    return {
        "issues": issues,
        "warnings": warnings,
        "is_valid": len(issues) == 0
    }

def fix_manim_code(code: str) -> str:
    """
    Automatically fix common Manim code issues
    """
    import re
    
    # Fix camera.frame issues - more comprehensive pattern matching
    # Pattern for self.camera.frame.animate with method chaining
    camera_pattern = r'self\.camera\.frame\.animate\.[^)]+\)'
    def replace_camera(match):
        # For camera animations, we'll replace with a simple wait instead
        return 'self.wait(0.5)  # Camera animation replaced with wait'
    code = re.sub(camera_pattern, replace_camera, code)
    
    # Fix any remaining broken syntax from camera replacements
    code = re.sub(r'self\.wait\(0\.5\)\s*# Camera animation replaced with wait\.[^)]+\)', 
                  'self.wait(0.5)  # Camera animation replaced with wait', code)
    
    # Also fix direct camera.frame usage
    code = code.replace("self.camera.frame.", "self.camera.frame_center.")
    
    # Fix font_size issues in get_tex
    # Pattern to match get_tex with font_size parameter
    pattern = r'\.get_tex\(([^)]+),\s*font_size=(\d+)\)'
    def replace_font_size(match):
        text = match.group(1)
        size = int(match.group(2))
        scale_factor = size / 36.0  # Default font size is 36
        return f'.get_tex({text}).scale({scale_factor:.2f})'
    code = re.sub(pattern, replace_font_size, code)
    
    # Fix problematic fonts
    code = code.replace('font="CMU Serif"', 'font="Arial"')
    code = code.replace('font="CMU Sans"', 'font="Arial"')
    code = code.replace('font="CMU Typewriter"', 'font="Courier New"')
    code = code.replace('font="Computer Modern"', 'font="Times New Roman"')
    
    # Fix ShowCreation
    code = code.replace("ShowCreation", "Create")
    
    # Remove SVGMobject usage
    if "SVGMobject" in code:
        # Replace with basic shapes - this is a simple replacement
        code = code.replace("SVGMobject", "Circle")  # Basic fallback
    
    return code

async def process_scene_phase3_async(session: aiohttp.ClientSession, overview: Dict[str, Any], scene: Dict[str, Any], api_key: str, scene_index: int, total_scenes: int, model: str = DEFAULT_MODEL) -> Dict[str, Any]:
    """
    Process a single scene through Phase 3 asynchronously to generate Manim-compatible code
    """
    print(f"\n📝 Processing scene {scene_index}/{total_scenes}: {scene.get('title', 'N/A')}")
    
    try:
        # Generate Manim code prompt for this scene
        prompt = generate_manim_code_prompt(overview, scene)
        
        # Call OpenAI API asynchronously
        response = await call_openai_api_async(session, prompt, api_key, model)
        
        # Parse JSON response
        try:
            code_data = json.loads(response)
        except json.JSONDecodeError as e:
            print(f"❌ Error parsing JSON for scene {scene_index}: {e}")
            # Fallback: create basic scene
            code_data = {
                "className": f"Scene{scene_index}",
                "filename": f"scene_{scene_index}.py",
                "code": f"# Error generating code for scene: {scene.get('title', 'N/A')}\n# {e}\nfrom manim import *\n\nclass Scene{scene_index}(Scene):\n    def construct(self):\n        title = Text(\"Scene {scene_index}\")\n        self.play(Write(title))\n        self.wait(2)",
                "validationResults": {
                    "syntaxValid": False,
                    "manimCompatible": False,
                    "warnings": [f"Failed to generate code: {e}"],
                    "suggestions": ["Retry code generation"]
                }
            }
        
        # Fix and validate the generated code
        code = code_data.get("code", "")
        code = fix_manim_code(code)  # Apply automatic fixes
        validation = validate_manim_code(code)
        
        # Add scene ID and create scene file entry
        scene_file = {
            "id": f"scene-{scene_index}",
            "className": code_data.get("className", f"Scene{scene_index}"),
            "filename": code_data.get("filename", f"scene_{scene_index}.py"),
            "code": code,
            "validationResults": {
                "syntaxValid": validation["is_valid"],
                "manimCompatible": validation["is_valid"],
                "warnings": validation["warnings"],
                "issues": validation["issues"],
                "suggestions": ["Fix API compatibility issues"] if not validation["is_valid"] else []
            }
        }
        
        # Print validation results
        if validation["issues"]:
            print(f"⚠️  Scene {scene_index} has issues: {', '.join(validation['issues'])}")
        if validation["warnings"]:
            print(f"ℹ️  Scene {scene_index} warnings: {', '.join(validation['warnings'])}")
        
        print(f"✅ Scene {scene_index} code generated successfully")
        return scene_file
        
    except (ValueError, KeyError, TypeError) as e:
        print(f"❌ Error processing scene {scene_index}: {e}")
        # Fallback: create basic scene
        scene_file = {
            "id": f"scene-{scene_index}",
            "className": f"Scene{scene_index}",
            "filename": f"scene_{scene_index}.py",
            "code": f"# Error generating code for scene: {scene.get('title', 'N/A')}\n# {e}\nfrom manim import *\n\nclass Scene{scene_index}(Scene):\n    def construct(self):\n        title = Text(\"Scene {scene_index}\")\n        self.play(Write(title))\n        self.wait(2)",
            "validationResults": {
                "syntaxValid": False,
                "manimCompatible": False,
                "warnings": [f"Failed to generate code: {e}"],
                "suggestions": ["Retry code generation"]
            }
        }
        return scene_file

async def process_scenes_phase3_async(scene_data: Dict[str, Any], api_key: str, model: str = DEFAULT_MODEL) -> Dict[str, Any]:
    """
    Process all scenes through Phase 3 in parallel to generate Manim-compatible code
    """
    print("\n🎬 PHASE 3: Generating Manim-compatible code (Parallel Processing)")
    print("="*70)
    
    overview = scene_data.get('overview', {})
    scenes = scene_data.get('scenes', [])
    
    # Create async session and process all scenes in parallel
    async with aiohttp.ClientSession() as session:
        tasks = []
        for i, scene in enumerate(scenes, 1):
            task = process_scene_phase3_async(session, overview, scene, api_key, i, len(scenes), model)
            tasks.append(task)
        
        # Wait for all tasks to complete with progress bar
        print(f"\n📝 Processing {len(scenes)} scenes in parallel...")
        scene_files = await tqdm.gather(*tasks, desc="Phase 3: Generating code", unit="scene")
        
        # Handle any exceptions that occurred
        processed_scene_files = []
        for i, result in enumerate(scene_files, 1):
            if isinstance(result, Exception):
                print(f"❌ Exception in scene {i}: {result}")
                # Create fallback scene file
                fallback_scene_file = {
                    "id": f"scene-{i}",
                    "className": f"Scene{i}",
                    "filename": f"scene_{i}.py",
                    "code": f"# Error generating code for scene: {scenes[i-1].get('title', 'N/A')}\n# {result}\nfrom manim import *\n\nclass Scene{i}(Scene):\n    def construct(self):\n        title = Text(\"Scene {i}\")\n        self.play(Write(title))\n        self.wait(2)",
                    "validationResults": {
                        "syntaxValid": False,
                        "manimCompatible": False,
                        "warnings": [f"Failed to generate code: {result}"],
                        "suggestions": ["Retry code generation"]
                    }
                }
                processed_scene_files.append(fallback_scene_file)
            else:
                processed_scene_files.append(result)
    
    # Generate master file content
    master_file_content = generate_master_file_content(overview, processed_scene_files)
    
    # Create Phase 3 output in the format expected by rendering
    phase3_data = {
        "lessonPlan": {
            "title": overview.get("title", "Generated Animation"),
            "objectives": overview.get("learning_objectives", [])
        },
        "sceneFiles": processed_scene_files,
        "masterFile": {
            "filename": "master_animation.py",
            "content": master_file_content
        },
        "totalScenes": len(processed_scene_files),
        "phase": 3,
        "processing_notes": "Scenes converted to Manim-compatible Python code (parallel processing)"
    }
    
    return phase3_data

def process_scenes_phase3(scene_data: Dict[str, Any], api_key: str, model: str = DEFAULT_MODEL) -> Dict[str, Any]:
    """
    Wrapper function to run the async Phase 3 processing
    """
    return asyncio.run(process_scenes_phase3_async(scene_data, api_key, model))

def generate_master_file_content(overview: Dict[str, Any], scene_files: List[Dict[str, Any]]) -> str:
    """
    Generate master file content similar to the rendering/result.json format
    """
    title = overview.get("title", "Generated Animation")
    
    return f"""# Master Manim Animation File
# Generated from AI lesson plan: {title}
from manim import *

class MasterExplainerScene(Scene):
    def construct(self):
        # Title slide for the lesson
        title = Text("{title}", font_size=48, color=WHITE)
        title.to_edge(UP, buff=0.5)
        
        subtitle = Text("Educational Animation Series", font_size=32, color=GRAY)
        subtitle.next_to(title, DOWN, buff=0.5)
        
        # Show title
        self.play(Write(title), run_time=2)
        self.play(FadeIn(subtitle), run_time=1)
        self.wait(2)
        
        # Scene list
        scene_list = VGroup()
        {chr(10).join([f'        scene_{i+1}_text = Text("Scene {i+1}: {scene["className"]}", font_size=24)\n        scene_list.add(scene_{i+1}_text)' for i, scene in enumerate(scene_files)])}
        
        scene_list.arrange(DOWN, aligned_edge=LEFT, buff=0.3)
        scene_list.next_to(subtitle, DOWN, buff=1)
        
        # Show scene list
        self.play(Write(scene_list), run_time=3)
        self.wait(2)
        
        # Fade out title slide
        self.play(FadeOut(title), FadeOut(subtitle), FadeOut(scene_list))
        self.wait(1)
        
        # Note: Individual scenes should be rendered separately
        # This master scene serves as an introduction/overview
        
        # End with a conclusion
        conclusion = Text("Thank you for watching!", font_size=36, color=WHITE)
        self.play(Write(conclusion), run_time=2)
        self.wait(2)
        self.play(FadeOut(conclusion))

if __name__ == "__main__":
    # Render the master overview scene
    master = MasterExplainerScene()
    master.render()
    
    # Individual scenes should be rendered separately:
    {chr(10).join([f'# python {scene["filename"]}' for scene in scene_files])}
"""

def render_videos(phase3_data: Dict[str, Any], output_dir: str) -> List[str]:
    """
    Render videos for each scene and return list of video paths
    """
    print("\n🎬 RENDERING VIDEOS")
    print("="*60)
    
    # Create necessary directories
    generated_dir = os.path.join(output_dir, "generated")
    mp4s_dir = os.path.join(output_dir, "mp4s")
    
    # Clean up and create directories
    shutil.rmtree(generated_dir, ignore_errors=True)
    os.makedirs(generated_dir, exist_ok=True)
    os.makedirs(mp4s_dir, exist_ok=True)
    
    # Generate Python files
    scene_files = phase3_data.get("sceneFiles", [])
    for file_data in scene_files:
        filename = file_data["filename"]
        code = file_data["code"]
        with open(os.path.join(generated_dir, filename), "w", encoding="utf-8") as f:
            f.write(code)
    
    # Generate master file
    master_file = phase3_data.get("masterFile", {})
    if master_file:
        with open(os.path.join(generated_dir, master_file["filename"]), "w", encoding="utf-8") as f:
            f.write(master_file["content"])
    
    # Change to generated directory for rendering
    original_cwd = os.getcwd()
    os.chdir(generated_dir)
    
    videos = []
    
    try:
        # Render master scene first
        master_filename = master_file.get("filename", "master_animation.py")
        master_class = "MasterExplainerScene"
        
        print(f"🎬 Rendering master scene: {master_filename}")
        try:
            subprocess.run(["manim", "-qm", master_filename, master_class], check=True)
            master_video = f"./media/videos/{master_filename.replace('.py', '')}/720p30/{master_class}.mp4"
            if os.path.exists(master_video):
                videos.append(master_video)
                print("✅ Master scene rendered successfully")
            else:
                print(f"⚠️  Master video file not found: {master_video}")
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            print(f"❌ Error rendering master scene: {e}")
        
        # Render individual scenes with progress bar
        print(f"\n🎬 Rendering {len(scene_files)} individual scenes...")
        for i, file_data in enumerate(tqdm(scene_files, desc="Rendering scenes", unit="scene"), 1):
            filename = file_data["filename"]
            class_name = file_data["className"]
            
            try:
                subprocess.run(["manim", "-qm", filename, class_name], check=True)
                video_path = f"./media/videos/{filename.replace('.py', '')}/720p30/{class_name}.mp4"
                if os.path.exists(video_path):
                    videos.append(video_path)
                    print(f"✅ Scene {i} rendered: {video_path}")
                else:
                    print(f"⚠️  Video file not found after rendering: {video_path}")
            except (subprocess.CalledProcessError, FileNotFoundError) as e:
                print(f"❌ Error rendering scene {i}: {e}")
        
        # Copy all videos to mp4s directory with proper naming
        print("\n📁 Copying videos to mp4s directory...")
        copied_videos = []
        
        # Copy master video first
        if videos and os.path.exists(videos[0]):
            master_dest = os.path.join(mp4s_dir, "master.mp4")
            shutil.copy2(videos[0], master_dest)
            copied_videos.append(master_dest)
            print(f"✅ Copied master video to: {master_dest}")
        
        # Copy individual scene videos
        for i, video_path in enumerate(tqdm(videos[1:], desc="Copying scene videos", unit="video"), 1):  # Skip master video
            if os.path.exists(video_path):
                scene_filename = f"scene_{i}.mp4"
                dest_path = os.path.join(mp4s_dir, scene_filename)
                shutil.copy2(video_path, dest_path)
                copied_videos.append(dest_path)
                print(f"✅ Copied scene {i} to: {dest_path}")
            else:
                print(f"⚠️  Source video not found: {video_path}")
        
        # Update videos list to point to copied files (convert to absolute paths)
        videos = [os.path.abspath(video) for video in copied_videos]
        
    finally:
        # Return to original directory
        os.chdir(original_cwd)
    
    return videos

def combine_videos(videos: List[str], output_dir: str) -> str:
    """
    Combine all videos into one complete video using ffmpeg
    """
    print("\n🎬 COMBINING VIDEOS")
    print("="*60)
    
    if not videos:
        print("❌ No videos to combine")
        return ""
    
    # Create videos list file for ffmpeg concat
    videos_list_path = os.path.join(output_dir, "generated", "videos_to_concat.txt")
    os.makedirs(os.path.dirname(videos_list_path), exist_ok=True)
    existing_videos = []
    
    with open(videos_list_path, "w", encoding="utf-8") as f:
        for video in videos:
            if os.path.exists(video):
                # Convert to absolute path for ffmpeg
                abs_video = os.path.abspath(video)
                f.write(f"file '{abs_video}'\n")
                existing_videos.append(abs_video)
                print(f"✅ Added video: {abs_video}")
            else:
                print(f"⚠️  Video not found: {video}")
    
    if not existing_videos:
        print("❌ No valid videos found to combine")
        return ""
    
    # Combine videos using ffmpeg
    output_video_path = os.path.join(output_dir, "complete.mp4")
    
    try:
        print("🎬 Combining videos with ffmpeg...")
        subprocess.run([
            "ffmpeg",
            "-f", "concat",
            "-safe", "0",
            "-i", videos_list_path,
            "-c", "copy",
            output_video_path
        ], check=True)
        
        print(f"✅ Complete video saved to: {output_video_path}")
        return output_video_path
        
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"❌ Error combining videos: {e}")
        return ""

def main():
    """
    Main function to run the scene generation process
    """
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Manim Explainer Scene Generator")
    parser.add_argument("-y", "--yes", action="store_true", 
                       help="Skip all confirmation prompts and proceed automatically")
    parser.add_argument("--topic", type=str, 
                       help="Topic to explain (if not provided, will prompt for input)")
    parser.add_argument("--model", type=str, default=DEFAULT_MODEL,
                       help=f"OpenAI model to use (default: {DEFAULT_MODEL})")
    args = parser.parse_args()
    
    # Load environment variables from .env file
    load_dotenv(dotenv_path="../.env")
    
    print("🎬 Manim Explainer Scene Generator")
    print("="*50)
    print(f"🤖 Using OpenAI model: {args.model}")
    
    # Get user input
    if args.topic:
        topic = args.topic.strip()
        print(f"Using topic from command line: {topic}")
    else:
        topic = input("Enter the topic you want to create an animation about (e.g., Pythagoras, BFS, DP): ").strip()
    
    if not topic:
        print("❌ Error: Please provide a topic.")
        return
    
    # Get OpenAI API key
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ Error: Please set your OPENAI_API_KEY environment variable.")
        print("You can either:")
        print("  1. Set it in a .env file: OPENAI_API_KEY=your-key-here")
        print("  2. Export it: export OPENAI_API_KEY=your-key-here")
        print("Get an API key from: https://platform.openai.com/api-keys")
        return
    
    print(f"\n🤖 Generating scene map for: {topic}")
    print("This may take a moment...")
    
    try:
        # Generate prompt
        prompt = generate_scene_prompt(topic)
        
        # Call OpenAI API
        response = call_openai_api(prompt, api_key, args.model)
        
        # Parse JSON response
        try:
            scene_data = json.loads(response)
        except json.JSONDecodeError as e:
            print(f"❌ Error parsing JSON response: {e}")
            print("Raw response:")
            print(response)
            return
        
        # Save Phase 1 to file
        phase1_output_path = "/home/zanger/Documents/cs/m-ai-nim/py_par/outputs/scene_map_phase_1.json"
        save_scene_map(scene_data, phase1_output_path)
        
        # Print Phase 1 results
        print_scene_map(scene_data)
        
        print("\n✅ Phase 1 completed successfully!")
        print("📁 Phase 1 output saved to:", phase1_output_path)
        
        # Ask user if they want to proceed to Phase 2
        proceed = get_user_input("\n🎬 Proceed to Phase 2 (detailed script generation)?", args.yes)
        
        if proceed:
            # Process Phase 2
            phase2_data = process_scenes_phase2(scene_data, api_key, args.model)
            
            # Save Phase 2 to file
            phase2_output_path = "/home/zanger/Documents/cs/m-ai-nim/py_par/outputs/scene_map_phase_2.json"
            save_scene_map(phase2_data, phase2_output_path)
            
            # Print Phase 2 results
            print_scene_map(phase2_data)
            print_phase2_summary(phase2_data)
            
            print("\n✅ Phase 2 completed successfully!")
            print("📁 Phase 2 output saved to:", phase2_output_path)
            
            # Ask user if they want to proceed to Phase 3
            proceed_phase3 = get_user_input("\n🎬 Proceed to Phase 3 (Manim code generation and video rendering)?", args.yes)
            
            if proceed_phase3:
                # Process Phase 3
                phase3_data = process_scenes_phase3(phase2_data, api_key, args.model)
                
                # Save Phase 3 to file
                phase3_output_path = "/home/zanger/Documents/cs/m-ai-nim/py_par/outputs/scene_map_phase_3_results.json"
                save_scene_map(phase3_data, phase3_output_path)
                
                print("\n✅ Phase 3 code generation completed!")
                print("📁 Phase 3 output saved to:", phase3_output_path)
                
                # Ask user if they want to render videos
                render_videos_choice = get_user_input("\n🎬 Render videos and create complete animation?", args.yes)
                
                if render_videos_choice:
                    # Render videos
                    output_dir = "/home/zanger/Documents/cs/m-ai-nim/py_par/outputs"
                    videos = render_videos(phase3_data, output_dir)
                    
                    if videos:
                        # Combine videos
                        complete_video = combine_videos(videos, output_dir)
                        
                        if complete_video:
                            print(f"\n🎉 Complete animation saved to: {complete_video}")
                        else:
                            print("\n❌ Failed to combine videos")
                    else:
                        print("\n❌ No videos were rendered successfully")
                else:
                    print("\n⏭️  Skipping video rendering. You can run the script again later to render videos.")
            else:
                print("\n⏭️  Skipping Phase 3. You can run the script again later to process Phase 3.")
        else:
            print("\n⏭️  Skipping Phase 2. You can run the script again later to process Phase 2.")
        
        print("\n🎉 All processing completed!")
        
    except (json.JSONDecodeError, FileNotFoundError, PermissionError, ValueError) as e:
        print("❌ Error during scene generation:", e)
        return

if __name__ == "__main__":
    main()
