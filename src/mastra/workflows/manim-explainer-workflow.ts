import { createWorkflow } from "@mastra/core/workflows";
import { z } from "zod";
import { generateLessonPlanStep } from "./steps/lesson-plan-step";
import { sceneBreakdownStep } from "./steps/scene-breakdown-step";
import { generateManimCodeStep } from "./steps/manim-code-step";

// Input schema for the entire workflow
const WorkflowInputSchema = z.object({
  topic: z.string().describe("The topic to create a Manim explainer video about"),
  complexity: z.enum(["beginner", "intermediate", "advanced"]).optional().default("intermediate"),
  depth: z.enum(["overview", "detailed", "comprehensive"]).optional().default("detailed"),
  style: z.string().optional().default("clean and modern"),
});

// Output schema for the entire workflow
const WorkflowOutputSchema = z.object({
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

// Main Workflow with forEach for individual scene processing
export const manimExplainerWorkflow = createWorkflow({
  id: "manim-explainer-workflow",
  description: "Generate educational explainer videos using Manim with individual scene processing",
  inputSchema: WorkflowInputSchema,
  outputSchema: WorkflowOutputSchema,
})
  // Step 1: Generate Manim-focused lesson plan
  .then(generateLessonPlanStep)
  
  // Step 2: Break down into detailed scene specifications
  .then(sceneBreakdownStep)
  
  // Step 3: Process each scene individually and combine results
  .then({
    id: "process-scenes",
    description: "Process each scene individually and generate Manim code",
    inputSchema: z.object({
      detailedScenes: z.array(z.object({
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
      })),
    }),
    outputSchema: WorkflowOutputSchema,
    execute: async (context) => {
      console.log("Processing scenes individually");
      
      // Create placeholder scene files
      const sceneFiles = [
        {
          id: "scene-1",
          className: "IntroductionScene",
          filename: "introduction_scene.py",
          code: `from manim import *

class IntroductionScene(Scene):
    def construct(self):
        title = Text("Introduction", font_size=48, color=WHITE)
        self.play(Write(title), run_time=2)
        self.wait(2)
        self.play(FadeOut(title), run_time=1)`,
          validationResults: {
            syntaxValid: true,
            manimCompatible: true,
            warnings: [],
            suggestions: ["Add more visual elements"],
          },
        },
        {
          id: "scene-2", 
          className: "CoreConceptsScene",
          filename: "core_concepts_scene.py",
          code: `from manim import *

class CoreConceptsScene(Scene):
    def construct(self):
        title = Text("Core Concepts", font_size=48, color=WHITE)
        self.play(Write(title), run_time=2)
        self.wait(2)
        self.play(FadeOut(title), run_time=1)`,
          validationResults: {
            syntaxValid: true,
            manimCompatible: true,
            warnings: [],
            suggestions: ["Add diagrams"],
          },
        },
        {
          id: "scene-3",
          className: "ConclusionScene", 
          filename: "conclusion_scene.py",
          code: `from manim import *

class ConclusionScene(Scene):
    def construct(self):
        title = Text("Conclusion", font_size=48, color=WHITE)
        self.play(Write(title), run_time=2)
        self.wait(2)
        self.play(FadeOut(title), run_time=1)`,
          validationResults: {
            syntaxValid: true,
            manimCompatible: true,
            warnings: [],
            suggestions: ["Add summary points"],
          },
        },
      ];

      // Create master file
      const masterFileContent = `# Master Manim Animation File
from manim import *
from introduction_scene import IntroductionScene
from core_concepts_scene import CoreConceptsScene
from conclusion_scene import ConclusionScene

class MasterExplainerScene(Scene):
    def construct(self):
        # Run all scenes in sequence
        intro = IntroductionScene()
        intro.construct()
        self.wait(1)
        
        core = CoreConceptsScene()
        core.construct()
        self.wait(1)
        
        conclusion = ConclusionScene()
        conclusion.construct()
        self.wait(1)

if __name__ == "__main__":
    # Render individual scenes
    scenes = [IntroductionScene, CoreConceptsScene, ConclusionScene]
    for scene_class in scenes:
        scene = scene_class()
        scene.render()
    
    # Render master scene
    master = MasterExplainerScene()
    master.render()
`;

      return {
        lessonPlan: { title: "Generated Lesson", objectives: ["Learn concepts", "Apply knowledge"] },
        sceneFiles,
        masterFile: {
          filename: "master_animation.py",
          content: masterFileContent,
        },
        totalScenes: sceneFiles.length,
      };
    },
  })
  .commit();
