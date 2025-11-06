/**
 * API Service for AdultingOS Mobile App
 *
 * Purpose:
 * - Provide a simple wrapper around fetch for talking to the backend APIs
 * - Centralize auth token handling and common headers
 * - Keep each endpoint simple and well-documented
 */

// Base URLs for the APIs
// TODO: Update these to point to your deployed backend or use environment variables
const API_BASE = 'http://127.0.0.1:8000'; // Django REST API
const ASSISTANT_BASE = 'http://127.0.0.1:8001'; // FastAPI Assistant

// In-memory auth token storage
let authToken = null;

/**
 * Set the authentication token for subsequent API requests
 */
export const setAuthToken = (token) => {
  authToken = token;
};

/**
 * Clear the authentication token
 */
export const clearAuthToken = () => {
  authToken = null;
};

/**
 * Generic request helper for Django API
 */
async function request(endpoint, options = {}) {
  const headers = {
    'Content-Type': 'application/json',
    ...options.headers,
  };

  if (authToken) {
    headers['Authorization'] = `Token ${authToken}`;
  }

  const config = {
    ...options,
    headers,
  };

  try {
    const response = await fetch(`${API_BASE}${endpoint}`, config);

    if (!response.ok) {
      let message = `HTTP ${response.status}: ${response.statusText}`;
      try {
        const maybeJson = await response.json();
        if (maybeJson && (maybeJson.detail || maybeJson.error)) {
          message = maybeJson.detail || maybeJson.error;
        }
      } catch (_) {
        // Response was not JSON
      }
      throw new Error(message);
    }

    return await response.json();
  } catch (error) {
    console.error('API request failed:', error);
    throw error;
  }
}

// Authentication endpoints
export const auth = {
  register: async (username, email, password) => {
    const response = await request('/api/auth/register/', {
      method: 'POST',
      body: JSON.stringify({
        username,
        email,
        password,
        password_confirm: password,
      }),
    });
    
    if (response.token) {
      setAuthToken(response.token);
    }
    
    return response;
  },

  login: async (username, password) => {
    const response = await request('/api/auth/login/', {
      method: 'POST',
      body: JSON.stringify({ username, password }),
    });
    
    if (response.token) {
      setAuthToken(response.token);
    }
    
    return response;
  },

  logout: () => {
    clearAuthToken();
  },
};

// Task management endpoints
export const tasks = {
  list: () => request('/api/tasks/'),

  create: (taskData) => request('/api/tasks/', {
    method: 'POST',
    body: JSON.stringify(taskData),
  }),

  update: (taskId, taskData) => request(`/api/tasks/${taskId}/`, {
    method: 'PUT',
    body: JSON.stringify(taskData),
  }),

  markComplete: (taskId) => request(`/api/tasks/${taskId}/mark_complete/`, {
    method: 'POST',
  }),

  markIncomplete: (taskId) => request(`/api/tasks/${taskId}/mark_incomplete/`, {
    method: 'POST',
  }),

  delete: (taskId) => request(`/api/tasks/${taskId}/`, {
    method: 'DELETE',
  }),
};

// Tag management endpoints
export const tags = {
  list: () => request('/api/tags/'),

  create: (name) => request('/api/tags/', {
    method: 'POST',
    body: JSON.stringify({ name }),
  }),
};

// User profile endpoints
export const profile = {
  get: () => request('/api/profile/me/'),

  update: (profileData) => request('/api/profile/me/', {
    method: 'PATCH',
    body: JSON.stringify(profileData),
  }),
};

// Assistant/Chat endpoints (FastAPI)
export const assistant = {
  chat: async (message) => {
    const headers = {
      'Content-Type': 'application/json',
    };

    if (authToken) {
      headers['Authorization'] = `Token ${authToken}`;
    }

    try {
      const response = await fetch(`${ASSISTANT_BASE}/chat`, {
        method: 'POST',
        headers,
        body: JSON.stringify({ message }),
      });

      if (!response.ok) {
        let message = `HTTP ${response.status}: ${response.statusText}`;
        try {
          const maybeJson = await response.json();
          if (maybeJson && (maybeJson.detail || maybeJson.error)) {
            message = maybeJson.detail || maybeJson.error;
          }
        } catch (_) {
          // Response was not JSON
        }
        throw new Error(message);
      }

      return await response.json();
    } catch (error) {
      console.error('Assistant API request failed:', error);
      throw error;
    }
  },
};

// Default export for convenience
export const apiService = {
  auth,
  tasks,
  tags,
  profile,
  assistant,
  setAuthToken,
  clearAuthToken,
};