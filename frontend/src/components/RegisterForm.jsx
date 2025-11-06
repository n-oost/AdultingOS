/**
 * RegisterForm.jsx
 *
 * A simple, readable registration form for the web app.
 * - Calls the API client `auth.register(username, email, password)`
 * - On success, calls `onRegisterSuccess(user, token)` provided by parent
 * - Shows clear validation and error messages
 */

import React, { useState } from 'react';
import { auth } from '../services/apiService';

export default function RegisterForm({ onRegisterSuccess }) {
  // Local state for the form fields and UI feedback
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirm, setConfirm] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  async function handleSubmit(e) {
    e.preventDefault(); // Prevent page reload
    setError('');
    setLoading(true);

    if (password !== confirm) {
      setError('Passwords do not match.');
      setLoading(false);
      return;
    }

    try {
      // Call the backend to register
      const result = await auth.register(username, email, password);
      // result: { user: { id, username, email }, token }

      // Let parent know we registered successfully
      onRegisterSuccess?.(result.user, result.token);
    } catch (err) {
      // Surface a friendly message
      setError(err?.message || 'Registration failed. Please try again.');
    } finally {
      setLoading(false);
    }
  }

  return (
    <form className="register-form" onSubmit={handleSubmit} autoComplete="on">
      {/* Error banner */}
      {error && <div className="error">{error}</div>}

      <div className="form-group">
        <label htmlFor="username">Username</label>
        <input
          id="username"
          type="text"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          autoComplete="username"
          placeholder="Enter your username"
          required
        />
      </div>

      <div className="form-group">
        <label htmlFor="email">Email</label>
        <input
          id="email"
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          autoComplete="email"
          placeholder="Enter your email"
          required
        />
      </div>

      <div className="form-group">
        <label htmlFor="password">Password</label>
        <input
          id="password"
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          autoComplete="new-password"
          placeholder="Enter your password"
          required
        />
      </div>

      <div className="form-group">
        <label htmlFor="confirm">Confirm Password</label>
        <input
          id="confirm"
          type="password"
          value={confirm}
          onChange={(e) => setConfirm(e.target.value)}
          autoComplete="new-password"
          placeholder="Confirm your password"
          required
        />
      </div>

      <div className="form-actions">
        <button className="btn" type="submit" disabled={loading}>
          {loading ? 'Registering...' : 'Register'}
        </button>
      </div>
    </form>
  );
}
