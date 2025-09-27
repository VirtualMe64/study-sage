import { createWorkflow } from "@mastra/core/workflows";
import { z } from "zod";
import { generateLessonPlanStep } from "./steps/lesson-plan-step";
import { processScenesStep } from "./steps/process-scenes-step";

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

// Clean workflow: Lesson Plan → Process Scenes → Generate Manim Files
export const manimExplainerWorkflow = createWorkflow({
  id: "manim-explainer-workflow",
  description: "Generate educational explainer videos using Manim - clean workflow",
  inputSchema: WorkflowInputSchema,
  outputSchema: WorkflowOutputSchema,
})
  // Step 1: Generate Manim-focused lesson plan
  .then(generateLessonPlanStep)
  
  // Step 2: Process each scene from lesson plan and generate Manim code
  .then(processScenesStep)
  .commit();
