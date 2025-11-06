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
import Input from '../ui/Input';
import Button from '../ui/Button';
import './AuthForms.css';

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
    <div className="auth-form">
      {/* Error banner */}
      {error && (
        <div className="auth-form__error" role="alert">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="12" cy="12" r="10"/>
            <line x1="12" y1="8" x2="12" y2="12"/>
            <line x1="12" y1="16" x2="12.01" y2="16"/>
          </svg>
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="auth-form__form">
        <Input
          id="username"
          type="text"
          label="Username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          autoComplete="username"
          placeholder="Enter your username"
          required
          leftIcon={
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
              <circle cx="12" cy="7" r="4"/>
            </svg>
          }
        />

        <Input
          id="password"
          type="password"
          label="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          autoComplete="current-password"
          placeholder="Enter your password"
          required
          leftIcon={
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/>
              <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
            </svg>
          }
        />

        <Button type="submit" variant="primary" fullWidth loading={loading}>
          {loading ? 'Logging in...' : 'Sign In'}
        </Button>
      </form>

      <p className="auth-form__hint">
        Tip: Use the credentials you created in the backend test (e.g., testuser / testpass123)
      </p>
    </div>
  );
}
