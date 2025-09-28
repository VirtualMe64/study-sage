const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

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
        throw new Error(data.error || `HTTP error! status: ${response.status}`);
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

  // Generate video using py_par/main.py
  async generateVideo({ topic, complexity, depth }) {
    return this.request('/videos/generate', {
      method: 'POST',
      body: JSON.stringify({
        topic,
        complexity,
        depth
      }),
    });
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

  // Check job status
  async getJobStatus(jobId) {
    return this.request(`/jobs/${jobId}`);
  }
}

const apiService = new ApiService();
export default apiService;
