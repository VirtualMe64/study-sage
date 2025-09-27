#!/usr/bin/env node

/**
 * Test script for the new scene-based outline workflow
 *
 * This script demonstrates the two-phase approach:
 * 1. Generate and refine outline
 * 2. Generate Manim code (after approval)
 */

import { mastra } from "./src/mastra/index.js";
import { generateOutlineWithJson } from "./src/mastra/utils/outline-json-generator.js";

async function testOutlineWorkflow() {
    console.log("🚀 Testing Scene-Based Outline Workflow\n");

    try {
        // Phase 1: Generate and refine outline
        console.log("📝 Phase 1: Generating scene-based outline...");

        const outlineResult =
            await mastra.workflows.manimOutlineWorkflow.execute({
                topic: "De Morgan's Laws in Boolean Logic",
                complexity: "intermediate",
                depth: "detailed",
                style: "clean and modern",
            });

        console.log("\n✅ Outline generation completed!");
        console.log(`Phase: ${outlineResult.phase}`);
        console.log(`Requires Approval: ${outlineResult.requiresApproval}`);
        console.log(
            `Scene Count: ${outlineResult.validation?.sceneCount || "N/A"}`
        );

        if (outlineResult.validation?.errors?.length > 0) {
            console.log("\n❌ Validation Errors:");
            outlineResult.validation.errors.forEach((error) =>
                console.log(`  - ${error}`)
            );
        }

        if (outlineResult.validation?.warnings?.length > 0) {
            console.log("\n⚠️ Validation Warnings:");
            outlineResult.validation.warnings.forEach((warning) =>
                console.log(`  - ${warning}`)
            );
        }

        // Display the generated outline
        if (outlineResult.outline?.rawOutline) {
            console.log("\n📋 Generated Outline:");
            console.log("=".repeat(50));
            console.log(outlineResult.outline.rawOutline);
            console.log("=".repeat(50));
        }

        // Generate JSON output
        if (outlineResult.outline) {
            console.log("\n📊 JSON Output:");
            const { jsonOutline } = generateOutlineWithJson(
                outlineResult.outline
            );
            console.log(JSON.stringify(jsonOutline, null, 2));
        }

        // Simulate approval and proceed to Phase 2
        if (outlineResult.requiresApproval && outlineResult.approvedOutline) {
            console.log("\n🎬 Phase 2: Generating Manim code...");

            const codeResult =
                await mastra.workflows.manimOutlineWorkflow.execute({
                    topic: "De Morgan's Laws in Boolean Logic",
                    complexity: "intermediate",
                    depth: "detailed",
                    style: "clean and modern",
                    skipToCodeGeneration: true,
                    approvedOutline: outlineResult.approvedOutline,
                });

            console.log("\n✅ Code generation completed!");
            console.log(`Total Scenes: ${codeResult.totalScenes}`);
            console.log(`Master File: ${codeResult.masterFile?.filename}`);

            if (codeResult.sceneFiles?.length > 0) {
                console.log("\n📁 Generated Scene Files:");
                codeResult.sceneFiles.forEach((scene) => {
                    console.log(`  - ${scene.filename} (${scene.className})`);
                });
            }
        } else {
            console.log(
                "\n⏸️ Outline ready for manual approval before code generation"
            );
        }
    } catch (error) {
        console.error("\n❌ Error during workflow execution:", error);
        process.exit(1);
    }
}

// Run the test
testOutlineWorkflow()
    .then(() => {
        console.log("\n🎉 Test completed successfully!");
        process.exit(0);
    })
    .catch((error) => {
        console.error("\n💥 Test failed:", error);
        process.exit(1);
    });
