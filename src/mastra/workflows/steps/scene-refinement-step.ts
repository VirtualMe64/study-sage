import { createStep } from "@mastra/core/workflows";
import { z } from "zod";
import { sceneRefinementAgent } from "../../agents/scene-refinement-agent";

// Schema for refined scene content
const refinedSceneSchema = z.object({
    number: z.number(),
    title: z.string(),
    objectives: z.string(),
    narration: z.string(),
    visualPlan: z.string(),
    animationPlan: z.string(),
    dependencies: z.string(),
    assessmentHook: z.string().optional(),
    rawContent: z.string(),
    // Enhanced fields from refinement
    preciseObjects: z.array(z.string()).optional(),
    orderedSteps: z.array(z.string()).optional(),
    timingHints: z.array(z.string()).optional(),
    continuityHooks: z
        .object({
            export: z.array(z.string()),
            import: z.array(z.string()),
        })
        .optional(),
    techNotes: z.array(z.string()).optional(),
});

const refinementOutputSchema = z.object({
    refinedScenes: z.array(refinedSceneSchema),
    rawRefinedOutline: z.string(),
});

// Parse refined scene content
function parseRefinedSceneContent(sceneText: string, sceneNumber: number): any {
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
    let preciseObjects: string[] = [];
    let orderedSteps: string[] = [];
    let timingHints: string[] = [];
    let continuityHooks = { export: [] as string[], import: [] as string[] };
    let techNotes: string[] = [];

    let currentSection = "";

    for (const line of lines) {
        if (line.startsWith("---SCENE:") && line.includes("|")) {
            const titleMatch = line.match(/---SCENE: \d+ \| (.+)---/);
            if (titleMatch) {
                title = titleMatch[1].trim();
            }
        } else if (line.startsWith("Objectives:")) {
            objectives = line.replace("Objectives:", "").trim();
            currentSection = "objectives";
        } else if (line.startsWith("Narration/On-screen:")) {
            narration = line.replace("Narration/On-screen:", "").trim();
            currentSection = "narration";
        } else if (line.startsWith("Visual plan:")) {
            visualPlan = line.replace("Visual plan:", "").trim();
            currentSection = "visual";
        } else if (line.startsWith("Animation plan:")) {
            animationPlan = line.replace("Animation plan:", "").trim();
            currentSection = "animation";
        } else if (line.startsWith("Dependencies:")) {
            dependencies = line.replace("Dependencies:", "").trim();
            currentSection = "dependencies";
        } else if (line.startsWith("Assessment hook:")) {
            assessmentHook = line.replace("Assessment hook:", "").trim();
            currentSection = "assessment";
        } else if (line.startsWith("**Precise objects (named ids):**")) {
            currentSection = "preciseObjects";
        } else if (line.startsWith("**Ordered animation steps:**")) {
            currentSection = "orderedSteps";
        } else if (line.startsWith("**Timing hints:**")) {
            currentSection = "timingHints";
        } else if (line.startsWith("**Continuity hooks:**")) {
            currentSection = "continuityHooks";
        } else if (line.startsWith("**Tech notes (Manim classes/methods):**")) {
            currentSection = "techNotes";
        } else if (
            line.startsWith("export:") &&
            currentSection === "continuityHooks"
        ) {
            const exportMatch = line.match(/export:\s*\[(.*?)\]/);
            if (exportMatch) {
                continuityHooks.export = exportMatch[1]
                    .split(",")
                    .map((s) => s.trim().replace(/['"]/g, ""))
                    .filter((s) => s.length > 0);
            }
        } else if (
            line.startsWith("import:") &&
            currentSection === "continuityHooks"
        ) {
            const importMatch = line.match(/import:\s*\[(.*?)\]/);
            if (importMatch) {
                continuityHooks.import = importMatch[1]
                    .split(",")
                    .map((s) => s.trim().replace(/['"]/g, ""))
                    .filter((s) => s.length > 0);
            }
        } else if (
            line.startsWith("- ") &&
            currentSection === "preciseObjects"
        ) {
            preciseObjects.push(line.replace("- ", "").trim());
        } else if (line.startsWith("- ") && currentSection === "orderedSteps") {
            orderedSteps.push(line.replace("- ", "").trim());
        } else if (line.startsWith("- ") && currentSection === "timingHints") {
            timingHints.push(line.replace("- ", "").trim());
        } else if (line.startsWith("- ") && currentSection === "techNotes") {
            techNotes.push(line.replace("- ", "").trim());
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
        preciseObjects: preciseObjects.length > 0 ? preciseObjects : undefined,
        orderedSteps: orderedSteps.length > 0 ? orderedSteps : undefined,
        timingHints: timingHints.length > 0 ? timingHints : undefined,
        continuityHooks:
            continuityHooks.export.length > 0 ||
            continuityHooks.import.length > 0
                ? continuityHooks
                : undefined,
        techNotes: techNotes.length > 0 ? techNotes : undefined,
    };
}

// Generate refinement prompt for a specific scene
function generateRefinementPrompt(scene: any): string {
    return `You are refining Scene ${scene.number} of a Manim video. Take the scene below and return the same scene with a deeper Visual plan and Animation plan suitable for direct Manim implementation. Keep the delimiter format.

Return the enhanced scene with:
- Precise objects (named ids)
- Ordered animation steps  
- Timing hints
- Continuity hooks
- Tech notes (Manim classes/methods)

${scene.rawContent}

Enhance the scene while maintaining the exact delimiter format and core educational objectives.`;
}

// Process scenes in parallel with concurrency limit
async function processScenesInParallel(
    scenes: any[],
    maxConcurrency: number = 4
): Promise<any[]> {
    const results: any[] = [];
    const errors: any[] = [];

    // Process scenes in batches to respect concurrency limits
    for (let i = 0; i < scenes.length; i += maxConcurrency) {
        const batch = scenes.slice(i, i + maxConcurrency);

        const batchPromises = batch.map(async (scene, index) => {
            try {
                console.log(
                    `🔧 Refining scene ${scene.number}: ${scene.title}`
                );

                const result = await sceneRefinementAgent.generateLegacy(
                    [
                        {
                            role: "user",
                            content: generateRefinementPrompt(scene),
                        },
                    ],
                    {
                        output: z.object({
                            content: z.string(),
                        }),
                    }
                );

                const refinedContent = result["object"].content;
                const parsedScene = parseRefinedSceneContent(
                    refinedContent,
                    scene.number
                );

                console.log(`✅ Scene ${scene.number} refined successfully`);
                return parsedScene;
            } catch (error) {
                console.error(
                    `❌ Error refining scene ${scene.number}:`,
                    error
                );
                errors.push({ sceneNumber: scene.number, error });
                // Return original scene if refinement fails
                return scene;
            }
        });

        const batchResults = await Promise.all(batchPromises);
        results.push(...batchResults);

        // Add delay between batches to respect rate limits
        if (i + maxConcurrency < scenes.length) {
            await new Promise((resolve) => setTimeout(resolve, 1000));
        }
    }

    if (errors.length > 0) {
        console.warn(
            `⚠️ ${errors.length} scenes had refinement errors, using original versions`
        );
    }

    return results;
}

export const sceneRefinementStep = createStep({
    id: "scene-refinement",
    description: "Refine scenes in parallel with enhanced technical details",
    inputSchema: z.object({
        outline: z.object({
            videoTitle: z.string(),
            scenes: z.array(
                z.object({
                    number: z.number(),
                    title: z.string(),
                    objectives: z.string(),
                    narration: z.string(),
                    visualPlan: z.string(),
                    animationPlan: z.string(),
                    dependencies: z.string(),
                    assessmentHook: z.string().optional(),
                    rawContent: z.string(),
                })
            ),
            rawOutline: z.string(),
        }),
    }),
    outputSchema: refinementOutputSchema,
    execute: async (params) => {
        console.log("🔧 Starting parallel scene refinement...");

        const outline = params["inputData"].outline;
        const scenes = outline.scenes;

        if (!scenes || scenes.length === 0) {
            throw new Error("No scenes found in outline for refinement");
        }

        try {
            // Process scenes in parallel with concurrency limit
            const refinedScenes = await processScenesInParallel(scenes, 4);

            // Sort by scene number to maintain order
            refinedScenes.sort((a, b) => a.number - b.number);

            // Reconstruct the raw outline from refined scenes
            let rawRefinedOutline = `# ${outline.videoTitle}\n\n`;

            for (const scene of refinedScenes) {
                rawRefinedOutline += scene.rawContent + "\n\n";
            }

            console.log(
                `✅ Scene refinement completed for ${refinedScenes.length} scenes`
            );

            return {
                refinedScenes,
                rawRefinedOutline,
            };
        } catch (error) {
            console.error("❌ Error during scene refinement:", error);
            throw error;
        }
    },
});
