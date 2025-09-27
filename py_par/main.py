#!/usr/bin/env python3
"""
Python version of the Manim Explainer Workflow
Generates scene-by-scene scripts for educational animations using OpenAI API
"""

import json
import os
from openai import OpenAI
from typing import Dict, Any
from dotenv import load_dotenv

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

Generate 3-5 scenes that would create an engaging educational Manim animation about {topic}.
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

def call_openai_api(prompt: str, api_key: str) -> str:
    """
    Call OpenAI API with the given prompt
    """
    try:
        client = OpenAI(api_key=api_key)
        
        response = client.chat.completions.create(
            model="gpt-4",
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
            temperature=0.7,
            max_tokens=4000
        )
        
        return response.choices[0].message.content.strip()
    
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

def process_scenes_phase2(scene_data: Dict[str, Any], api_key: str) -> Dict[str, Any]:
    """
    Process each scene through Phase 2 to add detailed script instructions
    """
    print("\n🎬 PHASE 2: Expanding scenes with detailed scripts")
    print("="*60)
    
    scenes = scene_data.get('scenes', [])
    expanded_scenes = []
    
    for i, scene in enumerate(scenes, 1):
        print(f"\n📝 Processing scene {i}/{len(scenes)}: {scene.get('title', 'N/A')}")
        
        try:
            # Generate detailed prompt for this scene
            prompt = generate_scene_script_prompt(scene)
            
            # Call OpenAI API
            response = call_openai_api(prompt, api_key)
            
            # Parse JSON response
            try:
                expanded_data = json.loads(response)
            except json.JSONDecodeError as e:
                print(f"❌ Error parsing JSON for scene {i}: {e}")
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
                expanded_scenes.append(expanded_scene)
                continue
            
            # Merge original scene with expanded data
            expanded_scene = scene.copy()
            expanded_scene['expanded_description'] = expanded_data.get('expanded_description', scene.get('description', ''))
            expanded_scene['script'] = expanded_data.get('script', {})
            
            expanded_scenes.append(expanded_scene)
            print(f"✅ Scene {i} expanded successfully")
            
        except (ValueError, KeyError, TypeError) as e:
            print(f"❌ Error processing scene {i}: {e}")
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
            expanded_scenes.append(expanded_scene)
    
    # Create Phase 2 output
    phase2_data = scene_data.copy()
    phase2_data['scenes'] = expanded_scenes
    phase2_data['phase'] = 2
    phase2_data['processing_notes'] = "Scenes expanded with detailed Manim script instructions"
    
    return phase2_data

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

def main():
    """
    Main function to run the scene generation process
    """
    # Load environment variables from .env file
    load_dotenv(dotenv_path="../.env")
    
    print("🎬 Manim Explainer Scene Generator")
    print("="*50)
    
    # Get user input
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
        response = call_openai_api(prompt, api_key)
        
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
        proceed = input("\n🎬 Proceed to Phase 2 (detailed script generation)? (y/n): ").strip().lower()
        
        if proceed in ['y', 'yes']:
            # Process Phase 2
            phase2_data = process_scenes_phase2(scene_data, api_key)
            
            # Save Phase 2 to file
            phase2_output_path = "/home/zanger/Documents/cs/m-ai-nim/py_par/outputs/scene_map_phase2.json"
            save_scene_map(phase2_data, phase2_output_path)
            
            # Print Phase 2 results
            print_scene_map(phase2_data)
            print_phase2_summary(phase2_data)
            
            print("\n✅ Phase 2 completed successfully!")
            print("📁 Phase 2 output saved to:", phase2_output_path)
        else:
            print("\n⏭️  Skipping Phase 2. You can run the script again later to process Phase 2.")
        
        print("\n🎉 All processing completed!")
        
    except (json.JSONDecodeError, FileNotFoundError, PermissionError, ValueError) as e:
        print("❌ Error during scene generation:", e)
        return

if __name__ == "__main__":
    main()
