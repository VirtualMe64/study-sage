import { Mastra } from "@mastra/core/mastra";
import { PinoLogger } from "@mastra/loggers";
import { LibSQLStore } from "@mastra/libsql";
import { manimExplainerWorkflow } from "./workflows/manim-explainer-workflow";
import { manimOutlineWorkflow } from "./workflows/manim-outline-workflow";
import { lessonPlanAgent } from "./agents/lesson-plan-agent";
import { manimCodeAgent } from "./agents/manim-code-agent";
import { outlineAgent } from "./agents/outline-agent";
import { sceneRefinementAgent } from "./agents/scene-refinement-agent";

export const mastra = new Mastra({
    workflows: {
        manimExplainerWorkflow,
        manimOutlineWorkflow,
    },
    agents: {
        lessonPlanAgent,
        manimCodeAgent,
        outlineAgent,
        sceneRefinementAgent,
    },
    storage: new LibSQLStore({
        // stores telemetry, evals, ... into memory storage, if it needs to persist, change to file:../mastra.db
        url: ":memory:",
    }),
    logger: new PinoLogger({
        name: "Mastra",
        level: "info",
    }),
});
