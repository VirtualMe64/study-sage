# Scene-Based Outline Workflow Usage

This document explains how to use the new scene-based, parallel outline refinement workflow for Manim video generation.

## Overview

The new workflow enforces a **two-phase approach**:

1. **Phase 1**: Outline & Scene Refinement (multi-round)
2. **Phase 2**: Manim code generation (only after outline approval)

## Workflow Components

### New Agents

- **`outlineAgent`**: Generates scene-based outlines with machine-parseable delimiters
- **`sceneRefinementAgent`**: Enhances scenes with technical details for Manim implementation
- **`manimCodeAgent`**: Updated with guardrails to prevent code generation before outline approval

### New Steps

- **`outlineGenerationStep`**: Creates first-pass scene-based outlines
- **`sceneRefinementStep`**: Processes scenes in parallel with concurrency limits
- **`outlineValidationStep`**: Validates scene structure and dependencies
- **`processScenesStep`**: Updated to work with approved outlines

### New Workflow

- **`manimOutlineWorkflow`**: Two-phase workflow with outline-first approach

## Scene Delimiter Format

Scenes use a machine-parseable format:

```
---SCENE: <number> | <optional short title>---
Objectives: <what this scene teaches>
Narration/On-screen: <key phrases, equations, labels>
Visual plan: <shapes, graphs, axes, constructions, highlights>
Animation plan: <entrances, transforms, reveals, timings, transitions>
Dependencies: <variables/objects from prior scenes>
Assessment hook: <quick check, intuition prompt>
---ENDSCENE---
```

## Usage Examples

### Basic Usage

```typescript
import { mastra } from "./src/mastra";

// Phase 1: Generate and refine outline
const result = await mastra.workflows.manimOutlineWorkflow.execute({
    topic: "Derivatives and Rate of Change",
    complexity: "intermediate",
    depth: "detailed",
    style: "clean and modern",
});

// Check if outline needs approval
if (result.requiresApproval) {
    console.log("Outline ready for review:");
    console.log(result.outline?.rawOutline);

    // After review and approval, proceed to code generation
    const codeResult = await mastra.workflows.manimOutlineWorkflow.execute({
        topic: "Derivatives and Rate of Change",
        complexity: "intermediate",
        depth: "detailed",
        style: "clean and modern",
        skipToCodeGeneration: true,
        approvedOutline: result.approvedOutline,
    });
}
```

### Advanced Usage with JSON Output

```typescript
import { generateOutlineWithJson } from "./src/mastra/utils/outline-json-generator";

const result = await mastra.workflows.manimOutlineWorkflow.execute({
    topic: "Boolean Logic and De Morgan's Laws",
    complexity: "beginner",
    depth: "comprehensive",
});

// Generate both text and JSON outputs
const { textOutline, jsonOutline } = generateOutlineWithJson(result.outline);

console.log("Text Outline:", textOutline);
console.log("JSON Outline:", JSON.stringify(jsonOutline, null, 2));
```

## Workflow Phases

### Phase 1: Outline Generation

1. **Outline Generation**: Creates scene-based outline with delimiters
2. **Scene Refinement**: Processes scenes in parallel (max 4 concurrent)
3. **Validation**: Checks structure, dependencies, and object naming
4. **Approval Required**: User must approve before code generation

### Phase 2: Code Generation

1. **Code Generation**: Creates Manim code from approved outline
2. **Master File**: Generates combined scene file
3. **Validation**: Ensures code quality and Manim compatibility

## Key Features

### Parallel Processing

- Scene refinements run in parallel with concurrency limits (default: 4)
- Exponential backoff for retry logic
- Graceful handling of individual scene failures

### Validation

- Scene numbering continuity
- Object name conflict detection
- Dependency resolution checking
- Technical implementation readiness

### Guardrails

- No code generation until outline approval
- Clear error messages for validation failures
- Structured feedback for improvements

## Error Handling

The workflow includes comprehensive error handling:

- **Validation Errors**: Block progression until fixed
- **Refinement Failures**: Use original scene if refinement fails
- **Code Generation Errors**: Continue with other scenes
- **Rate Limiting**: Built-in delays and retry logic

## JSON Output Format

The workflow can generate structured JSON alongside text outlines:

```json
{
    "video_title": "Derivatives and Rate of Change",
    "scenes": [
        {
            "number": 1,
            "title": "Intuition for Derivatives",
            "objectives": [
                "Build intuition for derivative as instantaneous rate of change"
            ],
            "narration": [
                "Slope of tangent line equals instantaneous rate of change"
            ],
            "visual_plan": [
                "Cartesian plane",
                "f(x)=x^2",
                "moving point P on curve"
            ],
            "animation_plan": [
                {
                    "step": 1,
                    "action": "Create axes",
                    "manim": ["Axes", "Create"]
                }
            ],
            "dependencies": [],
            "continuity_hooks": {
                "export": ["curve_f"],
                "import": []
            },
            "tech_notes": ["Use updaters for moving point"]
        }
    ]
}
```

## Migration from Old Workflow

To migrate from the old `manimExplainerWorkflow`:

1. Replace workflow reference: `manimOutlineWorkflow` instead of `manimExplainerWorkflow`
2. Handle the two-phase approach in your application logic
3. Implement approval mechanism for outline review
4. Update input/output schemas to match new structure

## Best Practices

1. **Always review outlines** before approving code generation
2. **Use specific topics** for better scene generation
3. **Iterate on outlines** if validation fails
4. **Monitor concurrency** for large numbers of scenes
5. **Validate dependencies** between scenes
6. **Use JSON output** for programmatic processing

## Troubleshooting

### Common Issues

- **Validation Failures**: Check scene numbering and object naming
- **Refinement Timeouts**: Reduce concurrency limit or add delays
- **Code Generation Errors**: Ensure outline is properly approved
- **Missing Dependencies**: Verify continuity hooks between scenes

### Debug Mode

Enable detailed logging by setting the logger level to 'debug' in the Mastra configuration.
