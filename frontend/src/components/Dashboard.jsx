/**
 * Dashboard Component
 * 
 * Main dashboard view with summary cards and quick actions.
 * Features a clean, banking-style interface with key metrics.
 */

import React, { useEffect, useState } from 'react';
import Card, { CardBody } from '../ui/Card';
import Button from '../ui/Button';
import { tasks } from '../services/apiService';
import './Dashboard.css';

export default function Dashboard({ user }) {
  const [stats, setStats] = useState({
    total: 0,
    completed: 0,
    pending: 0,
    overdue: 0
  });
  const [recentTasks, setRecentTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    loadDashboardData();
  }, []);

  async function loadDashboardData() {
    try {
      setLoading(true);
      setError('');
      const allTasks = await tasks.list();
      
      // Calculate stats
      const completed = allTasks.filter(t => t.completed).length;
      const pending = allTasks.filter(t => !t.completed).length;
      const overdue = allTasks.filter(t => t.is_overdue && !t.completed).length;
      
      setStats({
        total: allTasks.length,
        completed,
        pending,
        overdue
      });
      
      // Get recent tasks (top 5)
      setRecentTasks(allTasks.slice(0, 5));
    } catch (err) {
      console.error('Failed to load dashboard data:', err);
      setError(err?.message || 'Failed to load dashboard data. Please try again.');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="dashboard">
      {/* Welcome Section */}
      <div className="dashboard__welcome">
        <h2 className="dashboard__welcome-title">
          Welcome back, {user?.username || 'there'}! 👋
        </h2>
        <p className="dashboard__welcome-subtitle">
          Here's what's happening with your tasks today.
        </p>
      </div>

      {/* Error Message */}
      {error && (
        <div className="dashboard__error" role="alert">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="12" cy="12" r="10"/>
            <line x1="12" y1="8" x2="12" y2="12"/>
            <line x1="12" y1="16" x2="12.01" y2="16"/>
          </svg>
          {error}
        </div>
      )}

      {/* Stats Grid */}
      <div className="dashboard__stats">
        <Card variant="elevated" className="stat-card stat-card--primary">
          <CardBody>
            <div className="stat-card__icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <polyline points="9 11 12 14 22 4"/>
                <path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/>
              </svg>
            </div>
            <div className="stat-card__content">
              <div className="stat-card__label">Total Tasks</div>
              <div className="stat-card__value">
                {loading ? '—' : stats.total}
              </div>
            </div>
          </CardBody>
        </Card>

        <Card variant="elevated" className="stat-card stat-card--success">
          <CardBody>
            <div className="stat-card__icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
                <polyline points="22 4 12 14.01 9 11.01"/>
              </svg>
            </div>
            <div className="stat-card__content">
              <div className="stat-card__label">Completed</div>
              <div className="stat-card__value">
                {loading ? '—' : stats.completed}
              </div>
            </div>
          </CardBody>
        </Card>

        <Card variant="elevated" className="stat-card stat-card--info">
          <CardBody>
            <div className="stat-card__icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <circle cx="12" cy="12" r="10"/>
                <polyline points="12 6 12 12 16 14"/>
              </svg>
            </div>
            <div className="stat-card__content">
              <div className="stat-card__label">Pending</div>
              <div className="stat-card__value">
                {loading ? '—' : stats.pending}
              </div>
            </div>
          </CardBody>
        </Card>

        <Card variant="elevated" className="stat-card stat-card--warning">
          <CardBody>
            <div className="stat-card__icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <circle cx="12" cy="12" r="10"/>
                <line x1="12" y1="8" x2="12" y2="12"/>
                <line x1="12" y1="16" x2="12.01" y2="16"/>
              </svg>
            </div>
            <div className="stat-card__content">
              <div className="stat-card__label">Overdue</div>
              <div className="stat-card__value">
                {loading ? '—' : stats.overdue}
              </div>
            </div>
          </CardBody>
        </Card>
      </div>

      {/* Quick Actions */}
      <div className="dashboard__section">
        <h3 className="dashboard__section-title">Quick Actions</h3>
        <div className="dashboard__quick-actions">
          <Button variant="primary" size="lg">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <line x1="12" y1="5" x2="12" y2="19"/>
              <line x1="5" y1="12" x2="19" y2="12"/>
            </svg>
            Create Task
          </Button>
          <Button variant="secondary" size="lg">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
              <polyline points="17 8 12 3 7 8"/>
              <line x1="12" y1="3" x2="12" y2="15"/>
            </svg>
            Export Data
          </Button>
          <Button variant="outline" size="lg">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="12" cy="12" r="10"/>
              <line x1="2" y1="12" x2="22" y2="12"/>
              <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/>
            </svg>
            View Insights
          </Button>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="dashboard__section">
        <h3 className="dashboard__section-title">Recent Tasks</h3>
        <Card variant="default">
          <CardBody>
            {loading ? (
              <div className="dashboard__loading">Loading tasks...</div>
            ) : recentTasks.length === 0 ? (
              <div className="dashboard__empty">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
                  <line x1="9" y1="9" x2="15" y2="15"/>
                  <line x1="15" y1="9" x2="9" y2="15"/>
                </svg>
                <p>No tasks yet. Create your first task to get started!</p>
              </div>
            ) : (
              <ul className="dashboard__task-list">
                {recentTasks.map((task) => (
                  <li key={task.id} className="dashboard__task-item">
                    <div className="dashboard__task-checkbox">
                      {task.completed ? (
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                          <polyline points="20 6 9 17 4 12"/>
                        </svg>
                      ) : (
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                          <circle cx="12" cy="12" r="10"/>
                        </svg>
                      )}
                    </div>
                    <div className="dashboard__task-content">
                      <div className="dashboard__task-title">{task.title}</div>
                      {task.description && (
                        <div className="dashboard__task-description">{task.description}</div>
                      )}
                    </div>
                    {task.priority && (
                      <span className={`dashboard__task-priority dashboard__task-priority--${task.priority}`}>
                        P{task.priority}
                      </span>
                    )}
                  </li>
                ))}
              </ul>
            )}
          </CardBody>
        </Card>
      </div>
    </div>
  );
}
