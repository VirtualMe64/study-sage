import { createStep } from "@mastra/core/workflows";
import { z } from "zod";
import { outlineAgent } from "../../agents/outline-agent";

const generateOutlinePrompt = (
    topic: string,
    complexity: string,
    depth: string,
    style: string
) => {
    return `Create a comprehensive scene-based outline for a Manim educational video about "${topic}".

The lesson should be appropriate for ${complexity} level learners with ${depth} depth of coverage.

Requirements:
1. Generate 3-5 scenes using the exact delimiter format
2. Each scene must include all required fields (Objectives, Narration/On-screen text, Visual plan, Animation plan, Dependencies, Assessment hook)
3. Scenes should flow logically and build upon each other
4. Consider visual storytelling and mathematical animation best practices
5. Duration should be realistic for educational content (3-8 minutes total)
6. Use the exact scene delimiter format for machine parsing

Style preference: ${style}

Generate the outline using this exact format:

---SCENE: 1 | <title>---
Objectives: <what this scene teaches>
Narration/On-screen: <key phrases, equations, labels>
Visual plan: <shapes, graphs, axes, constructions, highlights>
Animation plan: <entrances, transforms, reveals, timings, transitions>
Dependencies: <variables/objects from prior scenes>
Assessment hook: <quick check, intuition prompt>
---ENDSCENE---

---SCENE: 2 | <title>---
[repeat format for each scene]
---ENDSCENE---

Continue for all scenes. Do NOT generate any Manim code - only the structured outline.`;
};

const sceneSchema = z.object({
    number: z.number(),
    title: z.string(),
    objectives: z.string(),
    narration: z.string(),
    visualPlan: z.string(),
    animationPlan: z.string(),
    dependencies: z.string(),
    assessmentHook: z.string().optional(),
    rawContent: z.string(), // Store the raw scene content for parsing
});

const outlineSchema = z.object({
    videoTitle: z.string(),
    scenes: z.array(sceneSchema),
    rawOutline: z.string(), // Store the complete raw outline text
});

const outputSchema = z.object({
    outline: outlineSchema,
});

// Parse scene content from raw text
function parseSceneContent(sceneText: string, sceneNumber: number): any {
    const lines = sceneText
        .split("\n")
        .map((line) => line.trim())
        .filter((line) => line.length > 0);

    let title = `Scene ${sceneNumber}`;
    let objectives = "";
    let narration = "";
    let visualPlan = "";
    let animationPlan = "";
    let dependencies = "";
    let assessmentHook = "";

    for (const line of lines) {
        if (line.startsWith("---SCENE:") && line.includes("|")) {
            const titleMatch = line.match(/---SCENE: \d+ \| (.+)---/);
            if (titleMatch) {
                title = titleMatch[1].trim();
            }
        } else if (line.startsWith("Objectives:")) {
            objectives = line.replace("Objectives:", "").trim();
        } else if (line.startsWith("Narration/On-screen:")) {
            narration = line.replace("Narration/On-screen:", "").trim();
        } else if (line.startsWith("Visual plan:")) {
            visualPlan = line.replace("Visual plan:", "").trim();
        } else if (line.startsWith("Animation plan:")) {
            animationPlan = line.replace("Animation plan:", "").trim();
        } else if (line.startsWith("Dependencies:")) {
            dependencies = line.replace("Dependencies:", "").trim();
        } else if (line.startsWith("Assessment hook:")) {
            assessmentHook = line.replace("Assessment hook:", "").trim();
        }
    }

    return {
        number: sceneNumber,
        title,
        objectives,
        narration,
        visualPlan,
        animationPlan,
        dependencies,
        assessmentHook: assessmentHook || undefined,
        rawContent: sceneText,
    };
}

// Parse the complete outline from raw text
function parseOutline(rawOutline: string): any {
    const scenes: any[] = [];
    const sceneRegex =
        /---SCENE: (\d+) \| (.+?)---\n([\s\S]*?)\n---ENDSCENE---/g;

    let match;
    while ((match = sceneRegex.exec(rawOutline)) !== null) {
        const sceneNumber = parseInt(match[1]);
        const sceneTitle = match[2].trim();
        const sceneContent = match[3].trim();

        const fullSceneText = `---SCENE: ${sceneNumber} | ${sceneTitle}---\n${sceneContent}\n---ENDSCENE---`;
        const parsedScene = parseSceneContent(fullSceneText, sceneNumber);
        scenes.push(parsedScene);
    }

    // Extract video title from the first line or use a default
    const lines = rawOutline.split("\n");
    const firstLine = lines[0]?.trim();
    const videoTitle =
        firstLine && !firstLine.startsWith("---SCENE:")
            ? firstLine
            : "Educational Video";

    return {
        videoTitle,
        scenes,
        rawOutline,
    };
}

export const outlineGenerationStep = createStep({
    id: "outline-generation",
    description: "Generate scene-based outline with delimiters for Manim video",
    inputSchema: z.object({
        topic: z
            .string()
            .describe("The topic to create an explainer video about"),
        complexity: z
            .enum(["beginner", "intermediate", "advanced"])
            .optional()
            .default("intermediate"),
        depth: z
            .enum(["overview", "detailed", "comprehensive"])
            .optional()
            .default("detailed"),
        style: z.string().optional().default("clean and modern"),
    }),
    outputSchema: outputSchema,
    execute: async (params) => {
        console.log("📝 Generating scene-based outline for:", params);

        const topic = params["inputData"].topic;
        const complexity = params["inputData"].complexity;
        const depth = params["inputData"].depth;
        const style = params["inputData"].style;

        try {
            // Use the outline agent to generate the structured outline
            const result = await outlineAgent.generateLegacy(
                [
                    {
                        role: "user",
                        content: generateOutlinePrompt(
                            topic,
                            complexity,
                            depth,
                            style
                        ),
                    },
                ],
                {
                    output: z.object({
                        content: z.string(),
                    }),
                }
            );

            const rawOutline = result["object"].content;
            console.log("✅ Raw outline generated, parsing scenes...");

            // Parse the outline into structured data
            const parsedOutline = parseOutline(rawOutline);

            console.log(
                `✅ Parsed outline with ${parsedOutline.scenes.length} scenes`
            );

            return {
                outline: parsedOutline,
            };
        } catch (error) {
            console.error("❌ Error generating outline:", error);
            throw error;
        }
    },
});
