import { createWorkflow } from "@mastra/core/workflows";
import { z } from "zod";
import { outlineGenerationStep } from "./steps/outline-generation-step";
import { sceneRefinementStep } from "./steps/scene-refinement-step";
import { outlineValidationStep } from "./steps/outline-validation-step";
import { processScenesStep } from "./steps/process-scenes-step";

// Input schema for the entire workflow
const WorkflowInputSchema = z.object({
    topic: z
        .string()
        .describe("The topic to create a Manim explainer video about"),
    complexity: z
        .enum(["beginner", "intermediate", "advanced"])
        .optional()
        .default("intermediate"),
    depth: z
        .enum(["overview", "detailed", "comprehensive"])
        .optional()
        .default("detailed"),
    style: z.string().optional().default("clean and modern"),
    // Optional: Skip to code generation if outline is already approved
    skipToCodeGeneration: z.boolean().optional().default(false),
    approvedOutline: z.any().optional(),
});

// Output schema for the entire workflow
const WorkflowOutputSchema = z.object({
    // Phase 1 outputs
    outline: z
        .object({
            videoTitle: z.string(),
            scenes: z.array(z.any()),
            rawOutline: z.string(),
        })
        .optional(),
    refinedOutline: z
        .object({
            refinedScenes: z.array(z.any()),
            rawRefinedOutline: z.string(),
        })
        .optional(),
    validation: z
        .object({
            isValid: z.boolean(),
            errors: z.array(z.string()),
            warnings: z.array(z.string()),
            suggestions: z.array(z.string()),
            sceneCount: z.number(),
            objectNames: z.array(z.string()),
            dependencies: z.array(z.string()),
        })
        .optional(),

    // Phase 2 outputs (only if code generation is approved)
    lessonPlan: z
        .object({
            title: z.string(),
            objectives: z.array(z.string()),
        })
        .optional(),
    sceneFiles: z
        .array(
            z.object({
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
            })
        )
        .optional(),
    masterFile: z
        .object({
            filename: z.string(),
            content: z.string(),
        })
        .optional(),
    totalScenes: z.number().optional(),

    // Workflow status
    phase: z.enum([
        "outline",
        "refinement",
        "validation",
        "code_generation",
        "complete",
    ]),
    requiresApproval: z.boolean(),
});

// Two-phase workflow: Outline & Scene Refinement → Code Generation
export const manimOutlineWorkflow = createWorkflow({
    id: "manim-outline-workflow",
    description:
        "Generate educational explainer videos using Manim with scene-based outline refinement",
    inputSchema: WorkflowInputSchema,
    outputSchema: WorkflowOutputSchema,
})
    // Phase 1: Outline Generation
    .then(outlineGenerationStep, {
        // Map input to outline generation
        input: (input) => ({
            topic: input.topic,
            complexity: input.complexity,
            depth: input.depth,
            style: input.style,
        }),
        // Map output for next step
        output: (output) => ({
            outline: output.outline,
        }),
    })

    // Phase 1: Scene Refinement (parallel processing)
    .then(sceneRefinementStep, {
        // Map outline output to refinement input
        input: (input) => ({
            outline: input.outline,
        }),
        // Map output for next step
        output: (output) => ({
            refinedOutline: output,
        }),
    })

    // Phase 1: Outline Validation
    .then(outlineValidationStep, {
        // Map refinement output to validation input
        input: (input) => ({
            refinedScenes: input.refinedOutline.refinedScenes,
            rawRefinedOutline: input.refinedOutline.rawRefinedOutline,
            videoTitle: input.outline.videoTitle,
        }),
        // Map output for conditional next step
        output: (output) => ({
            validation: output.validation,
            approvedOutline: output.approvedOutline,
        }),
    })

    // Phase 2: Code Generation (conditional - only if approved)
    .then(processScenesStep, {
        // Only proceed if validation passed and user approved
        condition: (input) => {
            return (
                input.validation?.isValid === true &&
                (input.skipToCodeGeneration === true || input.approvedOutline)
            );
        },
        // Map validation output to code generation input
        input: (input) => ({
            approvedOutline: input.approvedOutline,
        }),
        // Map final output
        output: (output) => ({
            lessonPlan: output.lessonPlan,
            sceneFiles: output.sceneFiles,
            masterFile: output.masterFile,
            totalScenes: output.totalScenes,
            phase: "complete",
            requiresApproval: false,
        }),
    })

    // Fallback for when code generation is not approved or validation fails
    .then({
        id: "outline-ready",
        description: "Outline ready for approval",
        inputSchema: z.object({
            outline: z.any(),
            refinedOutline: z.any(),
            validation: z.any(),
            approvedOutline: z.any(),
        }),
        outputSchema: z.object({
            phase: z.literal("validation"),
            requiresApproval: z.literal(true),
        }),
        execute: async (params) => {
            const validation = params["inputData"].validation;

            if (validation?.isValid === false) {
                console.log(
                    "❌ Outline validation failed. Please review and fix errors before proceeding."
                );
                return {
                    phase: "validation",
                    requiresApproval: true,
                };
            } else {
                console.log(
                    "✅ Outline ready for approval. Please review and approve before code generation."
                );
                return {
                    phase: "validation",
                    requiresApproval: true,
                };
            }
        },
    })
    .commit();
