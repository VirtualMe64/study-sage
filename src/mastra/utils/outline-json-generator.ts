import { z } from "zod";

// Schema for JSON output
const sceneJsonSchema = z.object({
    number: z.number(),
    title: z.string(),
    objectives: z.array(z.string()),
    narration: z.array(z.string()),
    visual_plan: z.array(z.string()),
    animation_plan: z.array(
        z.object({
            step: z.number(),
            action: z.string(),
            manim: z.array(z.string()),
        })
    ),
    dependencies: z.array(z.string()),
    continuity_hooks: z.object({
        export: z.array(z.string()),
        import: z.array(z.string()),
    }),
    tech_notes: z.array(z.string()),
});

const outlineJsonSchema = z.object({
    video_title: z.string(),
    scenes: z.array(sceneJsonSchema),
});

export type OutlineJson = z.infer<typeof outlineJsonSchema>;
export type SceneJson = z.infer<typeof sceneJsonSchema>;

// Convert scene outline to JSON format
export function convertSceneToJson(scene: any): SceneJson {
    // Parse objectives from string to array
    const objectives = scene.objectives
        ? scene.objectives
              .split(".")
              .map((obj: string) => obj.trim())
              .filter((obj: string) => obj.length > 0)
        : [];

    // Parse narration from string to array
    const narration = scene.narration
        ? scene.narration
              .split(",")
              .map((narr: string) => narr.trim())
              .filter((narr: string) => narr.length > 0)
        : [];

    // Parse visual plan from string to array
    const visual_plan = scene.visualPlan
        ? scene.visualPlan
              .split(",")
              .map((plan: string) => plan.trim())
              .filter((plan: string) => plan.length > 0)
        : [];

    // Parse animation plan into structured format
    const animation_plan = scene.orderedSteps
        ? scene.orderedSteps.map((step: string, index: number) => ({
              step: index + 1,
              action: step.trim(),
              manim: extractManimClasses(step),
          }))
        : [];

    // Parse dependencies from string to array
    const dependencies =
        scene.dependencies && scene.dependencies !== "None"
            ? scene.dependencies
                  .split(",")
                  .map((dep: string) => dep.trim())
                  .filter((dep: string) => dep.length > 0)
            : [];

    // Parse continuity hooks
    const continuity_hooks = scene.continuityHooks || {
        export: [],
        import: [],
    };

    // Parse tech notes
    const tech_notes = scene.techNotes || [];

    return {
        number: scene.number,
        title: scene.title,
        objectives,
        narration,
        visual_plan,
        animation_plan,
        dependencies,
        continuity_hooks,
        tech_notes,
    };
}

// Extract Manim class names from a step description
function extractManimClasses(step: string): string[] {
    const manimClasses = [
        "Axes",
        "NumberLine",
        "Graph",
        "Plot",
        "Text",
        "MathTex",
        "Tex",
        "VGroup",
        "Rectangle",
        "Circle",
        "Arrow",
        "Line",
        "Polygon",
        "Create",
        "FadeIn",
        "FadeOut",
        "Transform",
        "ReplacementTransform",
        "Write",
        "DrawBorderThenFill",
        "Succession",
        "AnimationGroup",
        "Wait",
    ];

    const foundClasses: string[] = [];
    const stepLower = step.toLowerCase();

    for (const manimClass of manimClasses) {
        if (stepLower.includes(manimClass.toLowerCase())) {
            foundClasses.push(manimClass);
        }
    }

    return foundClasses;
}

// Convert complete outline to JSON format
export function convertOutlineToJson(outline: any): OutlineJson {
    const scenes = outline.scenes.map((scene: any) =>
        convertSceneToJson(scene)
    );

    return {
        video_title: outline.videoTitle,
        scenes,
    };
}

// Generate JSON output alongside text outline
export function generateOutlineWithJson(outline: any): {
    textOutline: string;
    jsonOutline: OutlineJson;
} {
    const textOutline = outline.rawOutline || outline.rawRefinedOutline || "";
    const jsonOutline = convertOutlineToJson(outline);

    return {
        textOutline,
        jsonOutline,
    };
}
