/**
 * API Service for AdultingOS Web App
 *
 * Purpose:
 * - Provide a tiny, readable wrapper around fetch for talking to the Django API
 * - Centralize auth token handling and common headers
 * - Keep each endpoint simple and well-documented
 */

// Base URL for the API
// - In development, the CRA dev server and Django typically run on the same machine
// - You can override this with REACT_APP_API_URL in a .env file at the project root
//   Example: REACT_APP_API_URL=http://127.0.0.1:8000
const API_BASE = process.env.REACT_APP_API_URL || 'http://127.0.0.1:8000';

// In-memory auth token storage
// NOTE: This resets on page refresh. Persist to localStorage if you need durability.
let authToken = null;

/**
 * Set the authentication token for subsequent requests
 */
/**
 * Set the authentication token for subsequent API requests.
 * Call this after successful login/registration.
 */
export const setAuthToken = (token) => {
  authToken = token;
};

/**
 * Clear the authentication token (for logout)
 */
/**
 * Clear the authentication token (e.g., on logout).
 */
export const clearAuthToken = () => {
  authToken = null;
};

/**
 * Generic request helper.
 * - Automatically attaches JSON headers
 * - Adds Authorization header when a token is set
 * - Throws on non-2xx responses with a helpful message
 */
async function request(endpoint, options = {}) {
  const headers = {
    'Content-Type': 'application/json',
    ...options.headers,
  };

  // Add authentication token if available
  if (authToken) {
    headers['Authorization'] = `Token ${authToken}`;
  }

  const config = {
    ...options,
    headers,
  };

  try {
    const response = await fetch(`${API_BASE}${endpoint}`, config);

    // On error, try to surface a meaningful message from JSON body
    if (!response.ok) {
      let message = `HTTP ${response.status}: ${response.statusText}`;
      try {
        const maybeJson = await response.json();
        if (maybeJson && (maybeJson.detail || maybeJson.error)) {
          message = maybeJson.detail || maybeJson.error;
        }
      } catch (_) {
        // Response was not JSON; keep fallback message
      }
      throw new Error(message);
    }

    // Return JSON body for success responses
    return await response.json();
  } catch (error) {
    // Centralized error log for easier debugging
    console.error('API request failed:', error);
    throw error;
  }
}

// Authentication endpoints
export const auth = {
  /**
   * Register a new user
   */
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
    
    // Automatically set token after successful registration
    if (response.token) {
      setAuthToken(response.token);
    }
    
    return response;
  },

  /**
   * Login existing user
   */
  login: async (username, password) => {
    const response = await request('/api/auth/login/', {
      method: 'POST',
      body: JSON.stringify({ username, password }),
    });
    
    // Store token for future requests
    if (response.token) {
      setAuthToken(response.token);
    }
    
    return response;
  },

  /**
   * Logout user (client-side only for now)
   */
  logout: () => {
    clearAuthToken();
  },
};

// Task management endpoints
export const tasks = {
  /**
   * Get all tasks for authenticated user
   */
  list: () => request('/api/tasks/'),

  /**
   * Create a new task
   */
  create: (taskData) => request('/api/tasks/', {
    method: 'POST',
    body: JSON.stringify(taskData),
  }),

  /**
   * Update an existing task
   */
  update: (taskId, taskData) => request(`/api/tasks/${taskId}/`, {
    method: 'PUT',
    body: JSON.stringify(taskData),
  }),

  /**
   * Mark a task as complete
   */
  markComplete: (taskId) => request(`/api/tasks/${taskId}/mark_complete/`, {
    method: 'POST',
  }),

  /**
   * Mark a task as incomplete
   */
  markIncomplete: (taskId) => request(`/api/tasks/${taskId}/mark_incomplete/`, {
    method: 'POST',
  }),

  /**
   * Delete a task
   */
  delete: (taskId) => request(`/api/tasks/${taskId}/`, {
    method: 'DELETE',
  }),
};

// Tag management endpoints
export const tags = {
  /**
   * Get all tags
   */
  list: () => request('/api/tags/'),

  /**
   * Create a new tag
   */
  create: (name) => request('/api/tags/', {
    method: 'POST',
    body: JSON.stringify({ name }),
  }),
};

// Optional: named export for consumers who prefer a single object import
// Using a named constant avoids the ESLint warning about anonymous default exports.
export const api = { auth, tasks, tags, setAuthToken, clearAuthToken };