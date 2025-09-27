import { createStep } from "@mastra/core/workflows";
import { z } from "zod";

// Step 2: Break down scenes into detailed Manim specifications
export const sceneBreakdownStep = createStep({
  id: "scene-breakdown",
  description: "Break down each scene into detailed Manim animation specifications",
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
  outputSchema: z.object({
    detailedScenes: z.array(z.object({
      id: z.string(),
      title: z.string(),
      description: z.string(),
      manimElements: z.object({
        imports: z.array(z.string()).describe("Required Manim imports"),
        objects: z.array(z.string()).describe("Manim objects to create"),
        animations: z.array(z.string()).describe("Specific animations to use"),
        layout: z.string().describe("Scene layout and positioning"),
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
  execute: async (params) => {
    console.log("Breaking down scenes for Manim implementation");
    
    const scenes = [
      { title: "Introduction", description: "Introduction scene", manimConcepts: ["Text"], keyPoints: ["Intro"], estimatedDuration: 45 },
      { title: "Core Concepts", description: "Main concepts", manimConcepts: ["Graphs"], keyPoints: ["Concepts"], estimatedDuration: 90 },
      { title: "Conclusion", description: "Summary", manimConcepts: ["Summary"], keyPoints: ["Summary"], estimatedDuration: 30 }
    ];
    
    const detailedScenes = scenes.map((scene, index) => ({
      id: `scene-${index + 1}`,
      title: scene.title,
      description: scene.description,
      manimElements: {
        imports: ["from manim import *"],
        objects: ["Text", "VGroup", "Rectangle", "Circle", "Arrow"],
        animations: ["Write", "FadeIn", "Transform", "Create", "ShowCreation"],
        layout: "Centered with title at top, main content in middle, transitions between elements",
      },
      timing: {
        duration: scene.estimatedDuration,
        keyframes: [
          { time: 0, action: "scene_setup", description: "Initialize scene elements" },
          { time: 2, action: "title_animation", description: "Animate scene title" },
          { time: 5, action: "content_reveal", description: "Reveal main content" },
          { time: scene.estimatedDuration - 3, action: "conclusion", description: "Wrap up scene" },
        ],
      },
      visualStyle: {
        colors: ["#FFFFFF", "#3498db", "#e74c3c", "#2ecc71"],
        fonts: ["Arial", "Computer Modern"],
        theme: "dark",
      },
    }));

    return { detailedScenes };
  },
});
