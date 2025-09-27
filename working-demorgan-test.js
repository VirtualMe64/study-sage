#!/usr/bin/env node

/**
 * Working De Morgan's Laws Test
 *
 * This actually calls the real Mastra workflow
 */

console.log("🚀 Testing Real De Morgan's Laws Workflow\n");

// Let's try to fix the import issue by using a different approach
async function testWorkflow() {
    try {
        console.log("📦 Attempting to import Mastra module...");

        // Try to import the module and extract the mastra instance
        const module = await import("./.mastra/output/index.mjs");

        // The module might export mastra in different ways
        let mastra;
        if (module.mastra) {
            mastra = module.mastra;
        } else if (module.default && module.default.mastra) {
            mastra = module.default.mastra;
        } else {
            // Let's see what's actually exported
            console.log("Available exports:", Object.keys(module));
            console.log("Module structure:", typeof module);

            // Try to find mastra in the module
            for (const key of Object.keys(module)) {
                if (
                    key.includes("mastra") ||
                    (typeof module[key] === "object" &&
                        module[key] &&
                        module[key].workflows)
                ) {
                    console.log(`Found potential mastra at key: ${key}`);
                    mastra = module[key];
                    break;
                }
            }
        }

        if (!mastra) {
            throw new Error("Could not find mastra instance in module");
        }

        console.log("✅ Mastra module imported successfully!");
        console.log(
            "Available workflows:",
            Object.keys(mastra.workflows || {})
        );

        // Test the workflow
        console.log("\n📝 Calling manimOutlineWorkflow...");

        const result = await mastra.workflows.manimOutlineWorkflow.execute({
            topic: "De Morgan's Laws in Boolean Logic",
            complexity: "intermediate",
            depth: "detailed",
            style: "clean and modern",
        });

        console.log("✅ Workflow completed successfully!");
        console.log("\n📊 Results:");
        console.log("Phase:", result.phase);
        console.log("Requires Approval:", result.requiresApproval);

        if (result.outline) {
            console.log("\n📋 Generated Outline:");
            console.log("Title:", result.outline.videoTitle);
            console.log("Scenes:", result.outline.scenes.length);

            if (result.outline.rawOutline) {
                console.log("\nRaw Outline:");
                console.log("=".repeat(60));
                console.log(result.outline.rawOutline);
                console.log("=".repeat(60));
            }
        }

        if (result.validation) {
            console.log("\n🔍 Validation Results:");
            console.log("Valid:", result.validation.isValid);
            console.log("Errors:", result.validation.errors.length);
            console.log("Warnings:", result.validation.warnings.length);
            console.log("Suggestions:", result.validation.suggestions.length);
        }
    } catch (error) {
        console.error("❌ Error:", error.message);
        console.error("Stack:", error.stack);

        // Show what we found
        try {
            const module = await import("./.mastra/output/index.mjs");
            console.log("\n🔍 Debug info:");
            console.log("Available exports:", Object.keys(module));
            console.log("Module type:", typeof module);

            // Show first few keys in detail
            const keys = Object.keys(module).slice(0, 5);
            for (const key of keys) {
                console.log(`${key}:`, typeof module[key]);
            }
        } catch (importError) {
            console.error("Import error:", importError.message);
        }
    }
}

// Run the test
await testWorkflow();
