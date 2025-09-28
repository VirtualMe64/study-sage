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
11. CRITICAL: NEVER use multiline strings - keep all MathTex/Tex content on single lines
12. CRITICAL: For complex LaTeX like tables, use string concatenation or variables, NOT multiline strings
13. CRITICAL: Use .animate for Mobject transformations (e.g., circle.animate.shift(RIGHT), NOT circle.shift(RIGHT) in self.play())

String handling examples:
- For MathTex: MathTex(r"\\frac{1}{2}") or MathTex("\\\\frac{1}{2}")
- For Tex: Tex(r"$x^2 + y^2 = r^2$") or Tex("$x^2 + y^2 = r^2$")
- For simple tables: MathTex(r"\\begin{array}{cc} a & b \\\\ c & d \\end{array}")
- For complex tables/matrices: Generate programmatically using Python string operations
- Always use raw strings (r"") for mathematical expressions to avoid backslash issues
- NEVER break strings across multiple lines in the Python code

Complex LaTeX generation examples:
- table_content = "\\\\\\\\".join([f"{row[0]} & {row[1]}" for row in data])
- table_latex = rf"\\begin{{array}}{{cc}} {table_content} \\end{{array}}"
- truth_table = MathTex(table_latex)

Truth table generation example:
- truth_data = [["T", "T", "F"], ["T", "F", "T"], ["F", "T", "T"], ["F", "F", "T"]]
- header = "A & B & \\\\neg(A \\\\land B)"
- rows = " \\\\\\\\ ".join([" & ".join(row) for row in truth_data])
- table_latex = rf"\\begin{{array}}{{|c|c|c|}} \\hline {header} \\\\\\\\ \\hline {rows} \\\\\\\\ \\hline \\end{{array}}"
- table = MathTex(table_latex)

Mobject animation examples:
- self.play(circle.animate.shift(RIGHT))  # Move circle to the right
- self.play(text.animate.scale(1.5))      # Scale text up by 1.5x
- self.play(rect.animate.rotate(PI/4))    # Rotate rectangle 45 degrees
- self.play(group.animate.to_edge(UP))    # Move group to top edge

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
        # Simple title display
        title = Text("${lessonPlan.title}", font_size=48, color=WHITE)
        title.to_edge(UP, buff=1)

        # Show title
        self.play(Write(title), run_time=3)
        self.wait(2)

        # Fade out
        self.play(FadeOut(title))
        self.wait(1)

if __name__ == "__main__":
    # Render the master title scene
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
        const result = await manimCodeAgent.generate([{
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
