#!/usr/bin/env node

/**
 * Simple De Morgan's Laws Example
 *
 * This shows how to use the workflow programmatically
 */

// First, let's build the project
import { execSync } from "child_process";
import { readFileSync } from "fs";

console.log("🔨 Building Mastra project...");
try {
    execSync("npm run build", { stdio: "inherit" });
    console.log("✅ Build completed!\n");
} catch (error) {
    console.error("❌ Build failed:", error.message);
    process.exit(1);
}

// Now import the built module
console.log("📦 Importing built module...");
let mastra;
try {
    const { mastra: mastraInstance } = await import(
        "./.mastra/output/index.mjs"
    );
    mastra = mastraInstance;
    console.log("✅ Module imported successfully!\n");
} catch (error) {
    console.error("❌ Failed to import module:", error.message);
    process.exit(1);
}

async function runDeMorganExample() {
    console.log("🚀 De Morgan's Laws Example - Scene-Based Outline Workflow\n");

    try {
        // Phase 1: Generate and refine outline for De Morgan's Laws
        console.log(
            "📝 Phase 1: Generating scene-based outline for De Morgan's Laws..."
        );

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

        // Display validation results
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

        if (outlineResult.validation?.suggestions?.length > 0) {
            console.log("\n💡 Validation Suggestions:");
            outlineResult.validation.suggestions.forEach((suggestion) =>
                console.log(`  - ${suggestion}`)
            );
        }

        // Display the generated outline
        if (outlineResult.outline?.rawOutline) {
            console.log("\n📋 Generated Outline:");
            console.log("=".repeat(60));
            console.log(outlineResult.outline.rawOutline);
            console.log("=".repeat(60));
        }

        // Show scene details
        if (outlineResult.outline?.scenes) {
            console.log("\n🎬 Scene Details:");
            outlineResult.outline.scenes.forEach((scene, index) => {
                console.log(`\nScene ${scene.number}: ${scene.title}`);
                console.log(`  Objectives: ${scene.objectives}`);
                console.log(`  Visual Plan: ${scene.visualPlan}`);
                console.log(`  Animation Plan: ${scene.animationPlan}`);
                if (scene.preciseObjects?.length > 0) {
                    console.log(
                        `  Precise Objects: ${scene.preciseObjects.join(", ")}`
                    );
                }
                if (scene.orderedSteps?.length > 0) {
                    console.log(
                        `  Ordered Steps: ${scene.orderedSteps.join(" → ")}`
                    );
                }
            });
        }

        // Phase 2: Generate Manim code (if approved)
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
                    console.log(
                        `    Validation: ${scene.validationResults.syntaxValid ? "✅" : "❌"} Syntax, ${scene.validationResults.manimCompatible ? "✅" : "❌"} Manim`
                    );
                });
            }

            // Show a sample of the generated code
            if (codeResult.sceneFiles?.[0]?.code) {
                console.log("\n📝 Sample Generated Code (Scene 1):");
                console.log("-".repeat(40));
                const lines = codeResult.sceneFiles[0].code
                    .split("\n")
                    .slice(0, 20);
                console.log(lines.join("\n"));
                if (codeResult.sceneFiles[0].code.split("\n").length > 20) {
                    console.log("... (truncated)");
                }
                console.log("-".repeat(40));
            }
        } else {
            console.log(
                "\n⏸️ Outline ready for manual approval before code generation"
            );
            console.log("To proceed with code generation, you would need to:");
            console.log("1. Review the outline above");
            console.log(
                "2. Approve it by calling the workflow again with skipToCodeGeneration: true"
            );
        }
    } catch (error) {
        console.error("\n❌ Error during workflow execution:", error);
        console.error("Stack trace:", error.stack);
        process.exit(1);
    }
}

// Run the example
runDeMorganExample()
    .then(() => {
        console.log("\n🎉 De Morgan's Laws example completed successfully!");
        process.exit(0);
    })
    .catch((error) => {
        console.error("\n💥 Example failed:", error);
        process.exit(1);
    });
