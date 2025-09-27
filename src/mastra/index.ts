
import { Mastra } from '@mastra/core/mastra';
import { PinoLogger } from '@mastra/loggers';
import { LibSQLStore } from '@mastra/libsql';
import { manimExplainerWorkflow } from './workflows/manim-explainer-workflow';
import { lessonPlanAgent } from './agents/lesson-plan-agent';

export const mastra = new Mastra({
  workflows: { 
    manimExplainerWorkflow 
  },
  agents: { 
    lessonPlanAgent 
  },
  storage: new LibSQLStore({
    // stores telemetry, evals, ... into memory storage, if it needs to persist, change to file:../mastra.db
    url: ":memory:",
  }),
  logger: new PinoLogger({
    name: 'Mastra',
    level: 'info',
  }),
});
