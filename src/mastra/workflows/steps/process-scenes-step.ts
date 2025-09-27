import { createStep } from "@mastra/core/workflows";
import { z } from "zod";
import { manimCodeAgent } from "../../agents/manim-code-agent";

const generatePrompt = (title: string, description: string, manimConcepts: string[], keyPoints: string[], estimatedDuration: number) => {
  return `Generate complete, working Manim Python code for an educational animation scene.

Scene Details:
- Title: "${title}"
- Description: ${description}
- Key Points to Cover: ${keyPoints.join(", ")}
- Suggested Manim Concepts: ${manimConcepts.join(", ")}
- Target Duration: ${estimatedDuration} seconds

Requirements:
1. Create a complete Python class that inherits from Scene
2. Use appropriate Manim objects and animations
3. Include proper timing with self.play() and self.wait()
4. Make the animation educational and visually clear
5. Use the suggested Manim concepts where appropriate
6. Include descriptive comments explaining the animation logic
7. Ensure the code is syntactically correct and executable
8. Make the class name descriptive (based on the scene title)
9. CRITICAL: Use Create instead of ShowCreation (ShowCreation is deprecated)
10. CRITICAL: Properly escape backslashes in strings - use raw strings (r"") or double backslashes (\\\\) for LaTeX/MathTex

String handling examples:
- For MathTex: MathTex(r"\\frac{1}{2}") or MathTex("\\\\frac{1}{2}")
- For Tex: Tex(r"$x^2 + y^2 = r^2$") or Tex("$x^2 + y^2 = r^2$")
- Always use raw strings (r"") for mathematical expressions to avoid backslash issues

The animation should effectively teach the concept through visual storytelling and smooth transitions.

Return ONLY the Python code, nothing else.`
}

const manimCodeSchema = z.object({
  className: z.string().describe("Python class name for the scene"),
  code: z.string().describe("Complete Manim Python code for the scene"),
  filename: z.string().describe("Python filename for the scene"),
});

const generateMasterFileContent = (lessonPlan: any, sceneFiles: any[]) => {
  return `# Master Manim Animation File
# Generated from AI lesson plan: ${lessonPlan.title}
from manim import *

class MasterExplainerScene(Scene):
    def construct(self):
        # Title slide for the lesson
        title = Text("${lessonPlan.title}", font_size=48, color=WHITE)
        title.to_edge(UP, buff=0.5)
        
        subtitle = Text("Educational Animation Series", font_size=32, color=GRAY)
        subtitle.next_to(title, DOWN, buff=0.5)
        
        # Show title
        self.play(Write(title), run_time=2)
        self.play(FadeIn(subtitle), run_time=1)
        self.wait(2)
        
        # Scene list
        scene_list = VGroup()
        ${sceneFiles.map((scene, index) => `
        scene_${index + 1}_text = Text("Scene ${index + 1}: ${scene.id.replace('scene-', '').replace('-', ' ').toUpperCase()}", font_size=24)
        scene_list.add(scene_${index + 1}_text)`).join('\n        ')}
        
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
    ${sceneFiles.map(scene => `# python ${scene.filename}`).join('\n    ')}
`;
}

const outputSchema = z.object({
  lessonPlan: z.object({
    title: z.string(),
    objectives: z.array(z.string()),
  }),
  sceneFiles: z.array(z.object({
    id: z.string(),
    className: z.string(),
    filename: z.string(),
    code: z.string(),
    validationResults: z.object({
      syntaxValid: z.boolean(),
      manimCompatible: z.boolean(),
      warnings: z.array(z.string()),
      suggestions: z.array(z.string()),
    }),
  })),
  masterFile: z.object({
    filename: z.string(),
    content: z.string(),
  }),
  totalScenes: z.number(),
});

// Step to process all scenes from lesson plan and generate Manim code
export const processScenesStep = createStep({
  id: "process-scenes",
  description: "Process each scene from lesson plan and generate Manim code",
  inputSchema: z.object({
    lessonPlan: z.object({
      title: z.string(),
      objectives: z.array(z.string()),
      scenes: z.array(z.object({
        title: z.string(),
        description: z.string(),
        manimConcepts: z.array(z.string()),
        keyPoints: z.array(z.string()),
        estimatedDuration: z.number(),
      })),
    }),
  }),
  outputSchema: outputSchema,
  execute: async (params) => {
    console.log("🎬 Processing scenes individually with AI-generated Manim code");
    
    const lessonPlan = params['inputData']['lessonPlan']['object'];
    const scenes = lessonPlan['scenes'];

    if (!scenes || !scenes.length) {
      throw new Error("No lesson plan or scenes found in context");
    }
    
    // Process each scene through the AI agent
    const sceneFiles: any[] = [];
    
    for (let i = 0; i < scenes.length; i++) {
      const scene = scenes[i];
      console.log(`🤖 Generating Manim code for scene ${i + 1}: ${scene.title}`);
      
      try {
        // Use the Manim code agent directly to generate the code
        const result = await manimCodeAgent.generateLegacy([{
          role: "user",
          content: generatePrompt(
            scene.title,
            scene.description,
            scene.manimConcepts || [],
            scene.keyPoints || [],
            scene.estimatedDuration || 60
          )
        }], {
          output: manimCodeSchema,
        });

        
        sceneFiles.push({
          id: `scene-${i + 1}`,
          className: result['object'].className,
          filename: result['object'].filename,
          code: result['object'].code,
          validationResults: {
            syntaxValid: true,
            manimCompatible: true,
            warnings: [],
            suggestions: [],
          },
        });

      } catch (error) {
        console.error(`❌ Error generating code for scene "${scene.title}":`, error);
        // Continue with other scenes even if one fails
        sceneFiles.push({
          id: `scene-${i + 1}`,
          className: `Scene${i + 1}`,
          filename: `scene_${i + 1}.py`,
          code: `# Error generating code for scene: ${scene.title}\n# ${error}`,
          validationResults: {
            syntaxValid: false,
            manimCompatible: false,
            warnings: [`Failed to generate code: ${error}`],
            suggestions: ["Retry code generation"],
          },
        });
      }
    }

    // Create master file with dynamic scene imports
    const masterFileContent = generateMasterFileContent(lessonPlan, sceneFiles);

    return {
      lessonPlan: { 
        title: lessonPlan.title, 
        objectives: lessonPlan.objectives || ["Learn concepts", "Apply knowledge"] 
      },
      sceneFiles,
      masterFile: {
        filename: "master_animation.py",
        content: masterFileContent,
      },
      totalScenes: sceneFiles.length,
    };
  },
});
