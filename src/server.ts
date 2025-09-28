import express from 'express';
import cors from 'cors';
import { mastra } from './mastra/index.js';

const app = express();
const PORT = process.env.PORT || 3001;

// Middleware
app.use(cors({
  origin: 'http://localhost:3000', // React dev server
  credentials: true
}));
app.use(express.json());

// Health check endpoint
app.get('/api/health', (req, res) => {
  res.json({ status: 'ok', message: 'Mastra backend is running' });
});

// Workflow execution endpoint
app.post('/api/workflows/manim-explainer', async (req, res) => {
  try {
    const { topic, complexity, depth, style } = req.body;
    
    // Validate input
    if (!topic) {
      return res.status(400).json({ error: 'Topic is required' });
    }

    // Execute the workflow
    const result = await mastra.executeWorkflow('manimExplainerWorkflow', {
      topic,
      complexity: complexity || 'intermediate',
      depth: depth || 'detailed',
      style: style || 'clean and modern'
    });

    res.json({
      success: true,
      data: result
    });
  } catch (error) {
    console.error('Workflow execution error:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to execute workflow',
      details: error instanceof Error ? error.message : 'Unknown error'
    });
  }
});

// Agent execution endpoints
app.post('/api/agents/lesson-plan', async (req, res) => {
  try {
    const { topic, complexity, depth } = req.body;
    
    if (!topic) {
      return res.status(400).json({ error: 'Topic is required' });
    }

    const result = await mastra.agents.lessonPlanAgent.generate({
      messages: [{
        role: 'user',
        content: `Create a lesson plan for: ${topic}. Complexity: ${complexity || 'intermediate'}, Depth: ${depth || 'detailed'}`
      }]
    });

    res.json({
      success: true,
      data: result
    });
  } catch (error) {
    console.error('Agent execution error:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to execute lesson plan agent',
      details: error instanceof Error ? error.message : 'Unknown error'
    });
  }
});

app.post('/api/agents/manim-code', async (req, res) => {
  try {
    const { sceneDescription } = req.body;
    
    if (!sceneDescription) {
      return res.status(400).json({ error: 'Scene description is required' });
    }

    const result = await mastra.agents.manimCodeAgent.generate({
      messages: [{
        role: 'user',
        content: `Generate Manim code for this scene: ${sceneDescription}`
      }]
    });

    res.json({
      success: true,
      data: result
    });
  } catch (error) {
    console.error('Agent execution error:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to execute manim code agent',
      details: error instanceof Error ? error.message : 'Unknown error'
    });
  }
});

app.listen(PORT, () => {
  console.log(`🚀 Mastra backend server running on port ${PORT}`);
  console.log(`📡 API endpoints available at http://localhost:${PORT}/api`);
});
