/**
 * LoginForm.jsx
 *
 * A simple, readable login form for the web app.
 * - Calls the API client `auth.login(username, password)`
 * - On success, calls `onLoginSuccess(user, token)` provided by parent
 * - Shows clear validation and error messages
 */

import React, { useState } from 'react';
import { auth } from '../services/apiService';

export default function LoginForm({ onLoginSuccess }) {
  // Local state for the form fields and UI feedback
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  async function handleSubmit(e) {
    e.preventDefault(); // Prevent page reload
    setError('');
    setLoading(true);

    try {
      // Call the backend to authenticate
      const result = await auth.login(username, password);
      // result: { user: { id, username, email }, token }

      // Let parent know we logged in successfully
      onLoginSuccess?.(result.user, result.token);
    } catch (err) {
      // Surface a friendly message
      setError(err?.message || 'Login failed. Please try again.');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={{ maxWidth: 360, margin: '0 auto' }}>
      <h2>Login</h2>

      {/* Error banner */}
      {error && (
        <div style={{ background: '#fdecea', color: '#b00020', padding: 12, borderRadius: 6, marginBottom: 12 }}>
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit}>
        <label htmlFor="username">Username</label>
        <input
          id="username"
          type="text"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          autoComplete="username"
          placeholder="Enter your username"
          required
          style={{ width: '100%', padding: 8, margin: '6px 0 12px' }}
        />

        <label htmlFor="password">Password</label>
        <input
          id="password"
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          autoComplete="current-password"
          placeholder="Enter your password"
          required
          style={{ width: '100%', padding: 8, margin: '6px 0 12px' }}
        />

        <button type="submit" disabled={loading} style={{ width: '100%', padding: 10 }}>
          {loading ? 'Logging in...' : 'Login'}
        </button>
      </form>

      <p style={{ fontSize: 12, color: '#666', marginTop: 8 }}>
        Tip: Use the credentials you created in the backend test (e.g., testuser / testpass123)
      </p>
    </div>
  );
}
