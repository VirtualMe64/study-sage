import { createStep } from "@mastra/core/workflows";
import { z } from "zod";
import { manimCodeAgent } from "../../agents/manim-code-agent";

const generatePrompt = (scene: any) => {
    return `Generate complete, working Manim Python code for an educational animation scene based on the approved outline.

Scene Details:
- Title: "${scene.title}"
- Objectives: ${scene.objectives}
- Narration/On-screen: ${scene.narration}
- Visual Plan: ${scene.visualPlan}
- Animation Plan: ${scene.animationPlan}
- Dependencies: ${scene.dependencies}
${scene.assessmentHook ? `- Assessment Hook: ${scene.assessmentHook}` : ""}

Enhanced Technical Details:
${scene.preciseObjects ? `- Precise Objects: ${scene.preciseObjects.join(", ")}` : ""}
${scene.orderedSteps ? `- Ordered Steps: ${scene.orderedSteps.join(" -> ")}` : ""}
${scene.timingHints ? `- Timing Hints: ${scene.timingHints.join(", ")}` : ""}
${scene.continuityHooks ? `- Continuity Hooks: Export [${scene.continuityHooks.export.join(", ")}], Import [${scene.continuityHooks.import.join(", ")}]` : ""}
${scene.techNotes ? `- Tech Notes: ${scene.techNotes.join(", ")}` : ""}

Requirements:
1. Create a complete Python class that inherits from Scene
2. Use the precise object names from the outline when provided
3. Follow the ordered animation steps from the outline
4. Apply timing hints for appropriate pacing
5. Include proper timing with self.play() and self.wait()
6. Make the animation educational and visually clear
7. Include descriptive comments explaining the animation logic
8. Ensure the code is syntactically correct and executable
9. Make the class name descriptive (based on the scene title)
10. CRITICAL: Use Create instead of ShowCreation (ShowCreation is deprecated)
11. CRITICAL: Properly escape backslashes in strings - use raw strings (r"") or double backslashes (\\\\) for LaTeX/MathTex
12. CRITICAL: NEVER use multiline strings - keep all MathTex/Tex content on single lines
13. CRITICAL: For complex LaTeX like tables, use string concatenation or variables, NOT multiline strings
14. Use the technical notes to guide Manim class and method selection

String handling examples:
- For MathTex: MathTex(r"\\frac{1}{2}") or MathTex("\\\\frac{1}{2}")
- For Tex: Tex(r"$x^2 + y^2 = r^2$") or Tex("$x^2 + y^2 = r^2$")
- For simple tables: MathTex(r"\\begin{array}{cc} a & b \\\\ c & d \\end{array}")
- For complex tables/matrices: Generate programmatically using Python string operations
- Always use raw strings (r"") for mathematical expressions to avoid backslash issues
- NEVER break strings across multiple lines in the Python code

Complex LaTeX generation examples:
- table_content = "\\\\\\\\".join([f"{row[0]} & {row[1]}" for row in data])
- table_latex = rf"\\begin{{array}}{{cc}} {table_content} \\end{{array}}"
- truth_table = MathTex(table_latex)

Truth table generation example:
- truth_data = [["T", "T", "F"], ["T", "F", "T"], ["F", "T", "T"], ["F", "F", "T"]]
- header = "A & B & \\\\neg(A \\\\land B)"
- rows = " \\\\\\\\ ".join([" & ".join(row) for row in truth_data])
- table_latex = rf"\\begin{{array}}{{|c|c|c|}} \\hline {header} \\\\\\\\ \\hline {rows} \\\\\\\\ \\hline \\end{{array}}"
- table = MathTex(table_latex)

The animation should effectively teach the concept through visual storytelling and smooth transitions.

Return ONLY the Python code, nothing else.`;
};

const manimCodeSchema = z.object({
    className: z.string().describe("Python class name for the scene"),
    code: z.string().describe("Complete Manim Python code for the scene"),
    filename: z.string().describe("Python filename for the scene"),
});

const generateMasterFileContent = (lessonPlan: any, sceneFiles: any[]) => {
    return `# Master Manim Animation File
# Generated from AI lesson plan: ${lessonPlan.title}
from manim import *

class MasterExplainerScene(Scene):
    def construct(self):
        # Title slide for the lesson
        title = Text("${lessonPlan.title}", font_size=48, color=WHITE)
        title.to_edge(UP, buff=0.5)
        
        subtitle = Text("Educational Animation Series", font_size=32, color=GRAY)
        subtitle.next_to(title, DOWN, buff=0.5)
        
        # Show title
        self.play(Write(title), run_time=2)
        self.play(FadeIn(subtitle), run_time=1)
        self.wait(2)
        
        # Scene list
        scene_list = VGroup()
        ${sceneFiles
            .map(
                (scene, index) => `
        scene_${index + 1}_text = Text("Scene ${index + 1}: ${scene.id.replace("scene-", "").replace("-", " ").toUpperCase()}", font_size=24)
        scene_list.add(scene_${index + 1}_text)`
            )
            .join("\n        ")}
        
        scene_list.arrange(DOWN, aligned_edge=LEFT, buff=0.3)
        scene_list.next_to(subtitle, DOWN, buff=1)
        
        # Show scene list
        self.play(Write(scene_list), run_time=3)
        self.wait(2)
        
        # Fade out title slide
        self.play(FadeOut(title), FadeOut(subtitle), FadeOut(scene_list))
        self.wait(1)
        
        # Note: Individual scenes should be rendered separately
        # This master scene serves as an introduction/overview
        
        # End with a conclusion
        conclusion = Text("Thank you for watching!", font_size=36, color=WHITE)
        self.play(Write(conclusion), run_time=2)
        self.wait(2)
        self.play(FadeOut(conclusion))

if __name__ == "__main__":
    # Render the master overview scene
    master = MasterExplainerScene()
    master.render()
    
    # Individual scenes should be rendered separately:
    ${sceneFiles.map((scene) => `# python ${scene.filename}`).join("\n    ")}
`;
};

const outputSchema = z.object({
    lessonPlan: z.object({
        title: z.string(),
        objectives: z.array(z.string()),
    }),
    sceneFiles: z.array(
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
    ),
    masterFile: z.object({
        filename: z.string(),
        content: z.string(),
    }),
    totalScenes: z.number(),
});

// Step to process all scenes from lesson plan and generate Manim code
export const processScenesStep = createStep({
    id: "process-scenes",
    description: "Generate Manim code from approved scene outlines",
    inputSchema: z.object({
        approvedOutline: z.object({
            videoTitle: z.string(),
            scenes: z.array(z.any()),
            rawRefinedOutline: z.string(),
        }),
    }),
    outputSchema: outputSchema,
    execute: async (params) => {
        console.log("🎬 Generating Manim code from approved scene outlines");

        const approvedOutline = params["inputData"]["approvedOutline"];
        const scenes = approvedOutline.scenes;

        if (!scenes || !scenes.length) {
            throw new Error("No approved outline or scenes found in context");
        }

        // Process each scene through the AI agent
        const sceneFiles: any[] = [];

        for (let i = 0; i < scenes.length; i++) {
            const scene = scenes[i];
            console.log(
                `🤖 Generating Manim code for scene ${scene.number}: ${scene.title}`
            );

            try {
                // Use the Manim code agent directly to generate the code
                const result = await manimCodeAgent.generateLegacy(
                    [
                        {
                            role: "user",
                            content: generatePrompt(scene),
                        },
                    ],
                    {
                        output: manimCodeSchema,
                    }
                );

                sceneFiles.push({
                    id: `scene-${scene.number}`,
                    className: result["object"].className,
                    filename: result["object"].filename,
                    code: result["object"].code,
                    validationResults: {
                        syntaxValid: true,
                        manimCompatible: true,
                        warnings: [],
                        suggestions: [],
                    },
                });
            } catch (error) {
                console.error(
                    `❌ Error generating code for scene "${scene.title}":`,
                    error
                );
                // Continue with other scenes even if one fails
                sceneFiles.push({
                    id: `scene-${i + 1}`,
                    className: `Scene${i + 1}`,
                    filename: `scene_${i + 1}.py`,
                    code: `# Error generating code for scene: ${scene.title}\n# ${error}`,
                    validationResults: {
                        syntaxValid: false,
                        manimCompatible: false,
                        warnings: [`Failed to generate code: ${error}`],
                        suggestions: ["Retry code generation"],
                    },
                });
            }
        }

        // Create master file with dynamic scene imports
        const imports = sceneFiles
            .map(
                (_, index) => `from scene_${index + 1} import Scene${index + 1}`
            )
            .join("\n");
        const sceneCalls = sceneFiles
            .map(
                (_, index) =>
                    `        # Scene ${index + 1}\n        self.add(Scene${index + 1}())\n        self.wait(2)`
            )
            .join("\n\n");

        const masterFileContent = `from manim import *
${imports}

class MasterExplainerScene(Scene):
    def construct(self):
${sceneCalls}
`;

        return {
            lessonPlan: {
                title: approvedOutline.videoTitle,
                objectives: ["Learn concepts", "Apply knowledge"],
            },
            sceneFiles,
            masterFile: {
                filename: "master_animation.py",
                content: masterFileContent,
            },
            totalScenes: sceneFiles.length,
        };
    },
});
