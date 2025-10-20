/**
 * TasksList.jsx
 *
 * A simple, readable tasks screen for the web app.
 * - Lists user's tasks after login
 * - Allows creating and deleting tasks
 * - Uses the shared API client
 */

import React, { useEffect, useState } from 'react';
import { tasks } from '../services/apiService';

export default function TasksList() {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  // Minimal create form state
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');

  async function load() {
    try {
      setError('');
      setLoading(true);
      const data = await tasks.list();
      setItems(data);
    } catch (err) {
      setError(err?.message || 'Failed to load tasks');
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  async function handleCreate(e) {
    e.preventDefault();
    try {
      await tasks.create({ title, description });
      setTitle('');
      setDescription('');
      load();
    } catch (err) {
      alert(err?.message || 'Failed to create task');
    }
  }

  async function handleDelete(id) {
    if (!window.confirm('Delete this task?')) return;
    try {
      await tasks.delete(id);
      setItems((prev) => prev.filter((t) => t.id !== id));
    } catch (err) {
      alert(err?.message || 'Failed to delete task');
    }
  }

  return (
    <div>
      <div className="form-title">Your Tasks</div>

      {error && <div className="error">{error}</div>}

      {loading ? (
        <p>Loading...</p>
      ) : (
        <ul className="tasks-list">
          {items.map((t) => (
            <li className="task-item" key={t.id}>
              <span className="task-title">
                <strong>{t.title}</strong>
                {t.description ? ` — ${t.description}` : ''}
              </span>
              <button className="task-delete" onClick={() => handleDelete(t.id)}>Delete</button>
            </li>
          ))}
        </ul>
      )}

      <form onSubmit={handleCreate} style={{ marginTop: 24 }}>
        <div className="form-title" style={{ fontSize: '1.1rem', marginBottom: 10 }}>Create Task</div>
        <div className="form-group">
          <label htmlFor="task-title">Title</label>
          <input
            id="task-title"
            type="text"
            placeholder="Title"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            required
          />
        </div>
        <div className="form-group">
          <label htmlFor="task-desc">Description (optional)</label>
          <textarea
            id="task-desc"
            placeholder="Description"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            rows={2}
          />
        </div>
        <div className="form-actions">
          <button className="btn" type="submit">Create</button>
        </div>
      </form>
    </div>
  );
}
