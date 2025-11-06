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
import Input from '../ui/Input';
import Button from '../ui/Button';
import './TasksList.css';

export default function TasksList() {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  // Minimal create form state
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [creating, setCreating] = useState(false);

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
      setCreating(true);
      await tasks.create({ title, description });
      setTitle('');
      setDescription('');
      load();
    } catch (err) {
      setError(err?.message || 'Failed to create task');
    } finally {
      setCreating(false);
    }
  }

  async function handleDelete(id) {
    if (!window.confirm('Delete this task?')) return;
    try {
      await tasks.delete(id);
      setItems((prev) => prev.filter((t) => t.id !== id));
    } catch (err) {
      setError(err?.message || 'Failed to delete task');
    }
  }

  async function handleToggleComplete(task) {
    try {
      if (task.completed) {
        await tasks.markIncomplete(task.id);
      } else {
        await tasks.markComplete(task.id);
      }
      load();
    } catch (err) {
      setError(err?.message || 'Failed to update task');
    }
  }

  return (
    <div className="tasks-list-container">
      {error && (
        <div className="tasks-list__error" role="alert">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="12" cy="12" r="10"/>
            <line x1="12" y1="8" x2="12" y2="12"/>
            <line x1="12" y1="16" x2="12.01" y2="16"/>
          </svg>
          {error}
        </div>
      )}

      {loading ? (
        <div className="tasks-list__loading">
          <div className="tasks-list__spinner" />
          <p>Loading tasks...</p>
        </div>
      ) : items.length === 0 ? (
        <div className="tasks-list__empty">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
            <path d="M9 3v18"/>
            <path d="M15 3v18"/>
            <path d="M3 9h18"/>
            <path d="M3 15h18"/>
          </svg>
          <p>No tasks yet. Create your first task below!</p>
        </div>
      ) : (
        <ul className="tasks-list">
          {items.map((task) => (
            <li key={task.id} className={`task-item ${task.completed ? 'task-item--completed' : ''}`}>
              <button 
                className="task-item__checkbox"
                onClick={() => handleToggleComplete(task)}
                aria-label={task.completed ? 'Mark as incomplete' : 'Mark as complete'}
              >
                {task.completed ? (
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <polyline points="20 6 9 17 4 12"/>
                  </svg>
                ) : (
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <circle cx="12" cy="12" r="10"/>
                  </svg>
                )}
              </button>
              <div className="task-item__content">
                <div className="task-item__title">{task.title}</div>
                {task.description && (
                  <div className="task-item__description">{task.description}</div>
                )}
              </div>
              <Button 
                variant="destructive" 
                size="sm" 
                onClick={() => handleDelete(task.id)}
                aria-label={`Delete ${task.title}`}
              >
                Delete
              </Button>
            </li>
          ))}
        </ul>
      )}

      <div className="tasks-list__create">
        <h3 className="tasks-list__create-title">Create New Task</h3>
        <form onSubmit={handleCreate} className="tasks-list__create-form">
          <Input
            id="task-title"
            type="text"
            label="Title"
            placeholder="Enter task title"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            required
            leftIcon={
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <line x1="8" y1="6" x2="21" y2="6"/>
                <line x1="8" y1="12" x2="21" y2="12"/>
                <line x1="8" y1="18" x2="21" y2="18"/>
                <line x1="3" y1="6" x2="3.01" y2="6"/>
                <line x1="3" y1="12" x2="3.01" y2="12"/>
                <line x1="3" y1="18" x2="3.01" y2="18"/>
              </svg>
            }
          />
          <Input
            id="task-desc"
            type="text"
            label="Description"
            placeholder="Add a description (optional)"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            leftIcon={
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                <polyline points="14 2 14 8 20 8"/>
                <line x1="16" y1="13" x2="8" y2="13"/>
                <line x1="16" y1="17" x2="8" y2="17"/>
                <polyline points="10 9 9 9 8 9"/>
              </svg>
            }
          />
          <Button type="submit" variant="primary" fullWidth loading={creating}>
            Create Task
          </Button>
        </form>
      </div>
    </div>
  );
}
