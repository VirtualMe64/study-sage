import { config } from '../config';

const API_BASE_URL = config.API_BASE_URL;

class ApiService {
  async request(endpoint, options = {}) {
    const url = `${API_BASE_URL}${endpoint}`;
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    };

    try {
      const response = await fetch(url, config);
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || `HTTP error! status: ${response.status}`);
      }

      return data;
    } catch (error) {
      console.error('API request failed:', error);
      throw error;
    }
  }

  // Health check
  async healthCheck() {
    return this.request('/health');
  }

  // Generate complete lesson (all phases)
  async generateLesson({ topic, complexity, depth, style }) {
    return this.request('/lessons/generate', {
      method: 'POST',
      body: JSON.stringify({
        topic,
        complexity,
        depth,
        style
      }),
    });
  }

  // Generate Phase 1 only (basic scene mapping)
  async generatePhase1({ topic, complexity, depth, style }) {
    return this.request('/lessons/phase1', {
      method: 'POST',
      body: JSON.stringify({
        topic,
        complexity,
        depth,
        style
      }),
    });
  }

  // Generate Phase 2 only (detailed scripts)
  async generatePhase2(sceneData) {
    return this.request('/lessons/phase2', {
      method: 'POST',
      body: JSON.stringify({
        scene_data: sceneData
      }),
    });
  }

  // Generate Phase 3 only (Manim code)
  async generatePhase3(sceneData) {
    return this.request('/lessons/phase3', {
      method: 'POST',
      body: JSON.stringify({
        scene_data: sceneData
      }),
    });
  }

  // Render videos
  async renderVideos(phase3Data) {
    return this.request('/lessons/render', {
      method: 'POST',
      body: JSON.stringify({
        phase3_data: phase3Data
      }),
    });
  }

  // Check job status
  async getJobStatus(jobId) {
    return this.request(`/jobs/${jobId}`);
  }

  // List generated files
  async listFiles() {
    return this.request('/files');
  }

  // Download file
  async downloadFile(filename) {
    const response = await fetch(`${API_BASE_URL}/files/${filename}`);
    if (!response.ok) {
      throw new Error(`Failed to download file: ${response.statusText}`);
    }
    return response.blob();
  }

  // Get file URL for direct access
  getFileUrl(filename) {
    return `${API_BASE_URL}/files/${filename}`;
  }
}

const apiService = new ApiService();
export default apiService;
