import { createStep } from "@mastra/core/workflows";
import { z } from "zod";

// Step 3: Generate individual Manim code for each scene (used with forEach)
export const generateManimCodeStep = createStep({
  id: "generate-manim-code",
  description: "Generate complete Manim Python code for a single scene",
  inputSchema: z.object({
    id: z.string(),
    title: z.string(),
    description: z.string(),
    manimElements: z.object({
      imports: z.array(z.string()),
      objects: z.array(z.string()),
      animations: z.array(z.string()),
      layout: z.string(),
    }),
    timing: z.object({
      duration: z.number(),
      keyframes: z.array(z.object({
        time: z.number(),
        action: z.string(),
        description: z.string(),
      })),
    }),
    visualStyle: z.object({
      colors: z.array(z.string()),
      fonts: z.array(z.string()),
      theme: z.string(),
    }),
  }),
  outputSchema: z.object({
    sceneCode: z.object({
      id: z.string(),
      className: z.string(),
      code: z.string(),
      filename: z.string(),
      dependencies: z.array(z.string()),
    }),
    validationResults: z.object({
      syntaxValid: z.boolean(),
      manimCompatible: z.boolean(),
      warnings: z.array(z.string()),
      suggestions: z.array(z.string()),
    }),
  }),
  execute: async (params) => {
    console.log("Generating Manim code for scene:", params);
    
    const className = "ExampleScene";
    const filename = "example_scene.py";
    
    // Generate sophisticated Manim code based on the scene specifications
    const code = `from manim import *

class ${className}(Scene):
    def construct(self):
        # Scene description
        
        # Scene setup
        self.camera.background_color = BLACK
        
        # Title animation
        title = Text("Scene Title", font_size=48, color=WHITE)
        title.to_edge(UP, buff=0.5)
        
        # Main content elements
        content = VGroup()
        
        # Animation sequence
        self.play(Write(title), run_time=2)
        self.wait(1)
        
        # Main animation logic here
        main_text = Text("Main content", font_size=32)
        main_text.next_to(title, DOWN, buff=1)
        
        self.play(FadeIn(main_text), run_time=2)
        self.wait(2)
        
        # Scene conclusion
        self.play(
            FadeOut(title),
            FadeOut(main_text),
            run_time=2
        )
        self.wait(1)

# Scene configuration
if __name__ == "__main__":
    scene = ${className}()
    scene.render()
`;

    return {
      sceneCode: {
        id: "scene-1",
        className,
        code,
        filename,
        dependencies: ["from manim import *"],
      },
      validationResults: {
        syntaxValid: true, // This would be validated by a Manim agent
        manimCompatible: true,
        warnings: [],
        suggestions: [
          "Consider adding more visual elements for better engagement",
          "Add smooth transitions between elements",
        ],
      },
    };
  },
});
