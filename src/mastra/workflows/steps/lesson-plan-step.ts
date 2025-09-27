import { createStep } from "@mastra/core/workflows";
import { z } from "zod";
import { lessonPlanAgent } from "../../agents/lesson-plan-agent";

const generatePrompt = (topic: string, complexity: string, depth: string, style: string) => {
  return `Create a comprehensive lesson plan for creating a Manim educational video about "${topic}".

The lesson should be appropriate for ${complexity} level learners with ${depth} depth of coverage.

Requirements:
1. The lesson plan should be specifically designed for Manim animations
2. Each scene should specify which Manim animation concepts to use
3. Consider visual storytelling and mathematical animation best practices
4. Scenes should flow logically and build upon each other
5. Duration should be realistic for educational content (3-8 minutes total)

Style preference: ${style}

Generate 3-5 scenes that would create an engaging educational Manim animation about ${topic}.`
}

const lessonPlanSchema = z.object({
  title: z.string(),
  objectives: z.array(z.string()),
  scenes: z.array(z.object({
    title: z.string(),
    description: z.string(),
    manimConcepts: z.array(z.string()).describe("Specific Manim visual concepts to use"),
    keyPoints: z.array(z.string()),
    estimatedDuration: z.number().describe("Estimated duration in seconds"),
  })),
});

const outputSchema = z.object({
  lessonPlan: lessonPlanSchema,
});

// Step 1: Generate Manim-focused lesson plan
export const generateLessonPlanStep = createStep({
  id: "generate-lesson-plan",
  description: "Generate a structured lesson plan optimized for Manim animations",
  inputSchema: z.object({
    topic: z.string().describe("The topic to create an explainer video about"),
    complexity: z.enum(["beginner", "intermediate", "advanced"]).optional().default("intermediate"),
    depth: z.enum(["overview", "detailed", "comprehensive"]).optional().default("detailed"),
    style: z.string().optional().default("clean and modern"),
  }),
  outputSchema: outputSchema,
  execute: async (params) => {
    console.log("🤖 Generating AI-powered lesson plan using Mastra agent for:", params);
    // Try direct access to properties (based on linting error structure)
    const topic = params['inputData'].topic;
    const complexity = params['inputData'].complexity;  
    const depth = params['inputData'].depth;
    const style = params['inputData'].style;
    
    try {
      // Use the Mastra agent to generate the lesson plan
      const result = await lessonPlanAgent.generateLegacy([{
          role: "user",
          content: generatePrompt(topic, complexity, depth, style)
        }],
      {
        output: lessonPlanSchema,
      });

      console.log("✅ AI lesson plan generated successfully");
      
      return {
        lessonPlan: result as any, // Type assertion to handle Mastra's wrapped result type
      };
      
    } catch (error) {
      console.error("❌ Error generating lesson plan:", error);
      throw error; // Let it fail properly instead of fake fallback
    }
  },
});
