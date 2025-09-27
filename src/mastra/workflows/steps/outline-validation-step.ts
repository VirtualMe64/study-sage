import { createStep } from "@mastra/core/workflows";
import { z } from "zod";

const validationResultSchema = z.object({
    isValid: z.boolean(),
    errors: z.array(z.string()),
    warnings: z.array(z.string()),
    suggestions: z.array(z.string()),
    sceneCount: z.number(),
    objectNames: z.array(z.string()),
    dependencies: z.array(z.string()),
});

const validationOutputSchema = z.object({
    validation: validationResultSchema,
    approvedOutline: z.object({
        videoTitle: z.string(),
        scenes: z.array(z.any()),
        rawRefinedOutline: z.string(),
    }),
});

// Validate scene structure and dependencies
function validateOutline(refinedScenes: any[]): any {
    const errors: string[] = [];
    const warnings: string[] = [];
    const suggestions: string[] = [];
    const objectNames: string[] = [];
    const dependencies: string[] = [];

    // Check scene count and numbering
    if (refinedScenes.length === 0) {
        errors.push("No scenes found in outline");
    }

    // Check for contiguous numbering
    const sceneNumbers = refinedScenes
        .map((s) => s.number)
        .sort((a, b) => a - b);
    for (let i = 0; i < sceneNumbers.length; i++) {
        if (sceneNumbers[i] !== i + 1) {
            errors.push(
                `Scene numbering is not contiguous. Expected ${i + 1}, found ${sceneNumbers[i]}`
            );
        }
    }

    // Validate each scene
    for (const scene of refinedScenes) {
        // Check required fields
        if (!scene.title || scene.title.trim() === "") {
            errors.push(`Scene ${scene.number}: Missing or empty title`);
        }

        if (!scene.objectives || scene.objectives.trim() === "") {
            errors.push(`Scene ${scene.number}: Missing or empty objectives`);
        }

        if (!scene.visualPlan || scene.visualPlan.trim() === "") {
            errors.push(`Scene ${scene.number}: Missing or empty visual plan`);
        }

        if (!scene.animationPlan || scene.animationPlan.trim() === "") {
            errors.push(
                `Scene ${scene.number}: Missing or empty animation plan`
            );
        }

        // Collect object names for conflict checking
        if (scene.preciseObjects && Array.isArray(scene.preciseObjects)) {
            objectNames.push(...scene.preciseObjects);
        }

        // Collect dependencies
        if (
            scene.dependencies &&
            scene.dependencies.trim() !== "None" &&
            scene.dependencies.trim() !== ""
        ) {
            dependencies.push(scene.dependencies);
        }

        // Check for continuity hooks
        if (scene.continuityHooks) {
            if (
                scene.continuityHooks.export &&
                Array.isArray(scene.continuityHooks.export)
            ) {
                objectNames.push(...scene.continuityHooks.export);
            }
            if (
                scene.continuityHooks.import &&
                Array.isArray(scene.continuityHooks.import)
            ) {
                // These should be defined in previous scenes
                const importedObjects = scene.continuityHooks.import;
                const previousSceneNumbers = sceneNumbers.filter(
                    (n) => n < scene.number
                );
                if (
                    previousSceneNumbers.length === 0 &&
                    importedObjects.length > 0
                ) {
                    warnings.push(
                        `Scene ${scene.number}: Imports objects but has no previous scenes`
                    );
                }
            }
        }

        // Check for technical implementation readiness
        if (!scene.orderedSteps || scene.orderedSteps.length === 0) {
            warnings.push(
                `Scene ${scene.number}: No ordered animation steps provided`
            );
        }

        if (!scene.techNotes || scene.techNotes.length === 0) {
            warnings.push(`Scene ${scene.number}: No technical notes provided`);
        }

        // Check animation plan specificity
        if (scene.animationPlan && scene.animationPlan.length < 50) {
            suggestions.push(
                `Scene ${scene.number}: Animation plan could be more detailed`
            );
        }

        // Check visual plan specificity
        if (scene.visualPlan && scene.visualPlan.length < 50) {
            suggestions.push(
                `Scene ${scene.number}: Visual plan could be more detailed`
            );
        }
    }

    // Check for object name conflicts
    const objectNameCounts = objectNames.reduce(
        (acc, name) => {
            acc[name] = (acc[name] || 0) + 1;
            return acc;
        },
        {} as Record<string, number>
    );

    const conflictingObjects = Object.entries(objectNameCounts)
        .filter(([_, count]) => count > 1)
        .map(([name, _]) => name);

    if (conflictingObjects.length > 0) {
        errors.push(
            `Conflicting object names found: ${conflictingObjects.join(", ")}`
        );
    }

    // Check dependency resolution
    for (const scene of refinedScenes) {
        if (scene.continuityHooks && scene.continuityHooks.import) {
            const importedObjects = scene.continuityHooks.import;
            const previousScenes = refinedScenes.filter(
                (s) => s.number < scene.number
            );

            for (const importedObj of importedObjects) {
                const isDefinedInPreviousScenes = previousScenes.some(
                    (prevScene) => {
                        return (
                            (prevScene.preciseObjects &&
                                prevScene.preciseObjects.includes(
                                    importedObj
                                )) ||
                            (prevScene.continuityHooks &&
                                prevScene.continuityHooks.export &&
                                prevScene.continuityHooks.export.includes(
                                    importedObj
                                ))
                        );
                    }
                );

                if (!isDefinedInPreviousScenes) {
                    errors.push(
                        `Scene ${scene.number}: Imported object '${importedObj}' not defined in previous scenes`
                    );
                }
            }
        }
    }

    // Check for educational flow
    if (refinedScenes.length > 1) {
        for (let i = 1; i < refinedScenes.length; i++) {
            const currentScene = refinedScenes[i];
            const previousScene = refinedScenes[i - 1];

            if (
                currentScene.dependencies === "None" &&
                previousScene.dependencies !== "None"
            ) {
                suggestions.push(
                    `Scene ${currentScene.number}: Consider building on previous scene's concepts`
                );
            }
        }
    }

    const isValid = errors.length === 0;

    return {
        isValid,
        errors,
        warnings,
        suggestions,
        sceneCount: refinedScenes.length,
        objectNames: [...new Set(objectNames)], // Remove duplicates
        dependencies: [...new Set(dependencies)], // Remove duplicates
    };
}

export const outlineValidationStep = createStep({
    id: "outline-validation",
    description: "Validate refined outline structure and dependencies",
    inputSchema: z.object({
        refinedScenes: z.array(z.any()),
        rawRefinedOutline: z.string(),
        videoTitle: z.string(),
    }),
    outputSchema: validationOutputSchema,
    execute: async (params) => {
        console.log("🔍 Validating refined outline...");

        const refinedScenes = params["inputData"].refinedScenes;
        const rawRefinedOutline = params["inputData"].rawRefinedOutline;
        const videoTitle = params["inputData"].videoTitle;

        try {
            // Validate the outline
            const validation = validateOutline(refinedScenes);

            console.log(
                `✅ Validation completed: ${validation.isValid ? "PASSED" : "FAILED"}`
            );
            console.log(`   - Scenes: ${validation.sceneCount}`);
            console.log(`   - Errors: ${validation.errors.length}`);
            console.log(`   - Warnings: ${validation.warnings.length}`);
            console.log(`   - Suggestions: ${validation.suggestions.length}`);

            if (validation.errors.length > 0) {
                console.log("❌ Validation errors:");
                validation.errors.forEach((error) =>
                    console.log(`   - ${error}`)
                );
            }

            if (validation.warnings.length > 0) {
                console.log("⚠️ Validation warnings:");
                validation.warnings.forEach((warning) =>
                    console.log(`   - ${warning}`)
                );
            }

            if (validation.suggestions.length > 0) {
                console.log("💡 Validation suggestions:");
                validation.suggestions.forEach((suggestion) =>
                    console.log(`   - ${suggestion}`)
                );
            }

            return {
                validation,
                approvedOutline: {
                    videoTitle,
                    scenes: refinedScenes,
                    rawRefinedOutline,
                },
            };
        } catch (error) {
            console.error("❌ Error during outline validation:", error);
            throw error;
        }
    },
});
