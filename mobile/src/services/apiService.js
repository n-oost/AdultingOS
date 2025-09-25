/**
 * API Service - Handles communication with AdultingOS backend
 */

// Use your deployed Vercel URL or local development URL
const API_BASE_URL = __DEV__ 
  ? 'http://localhost:8001'  // Local development
  : 'https://your-project.vercel.app';  // Replace with your Vercel URL

class ApiService {
  constructor() {
    this.baseURL = API_BASE_URL;
  }

  async chat(message, history = []) {
    try {
      const response = await fetch(`${this.baseURL}/api/assistant/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message,
          history: history.slice(-10), // Keep last 10 messages for context
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('API Error:', error);
      throw error;
    }
  }

  async getTasks() {
    return this.chat('/task list');
  }

  async createTask(title, options = {}) {
    const { description, category, dueDate, priority, tags } = options;
    let command = `/task add "${title}"`;
    
    if (description) command += ` --desc "${description}"`;
    if (category) command += ` --cat "${category}"`;
    if (dueDate) command += ` --due "${dueDate}"`;
    if (priority) command += ` --priority ${priority}`;
    if (tags && tags.length) command += ` --tags ${tags.join(',')}`;

    return this.chat(command);
  }

  async completeTask(taskId) {
    return this.chat(`/task done ${taskId}`);
  }
}

export const apiService = new ApiService();