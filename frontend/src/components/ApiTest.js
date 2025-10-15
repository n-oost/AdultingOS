import React, { useState } from 'react';
import { auth, tasks } from '../services/apiService';

/**
 * Simple component to test API connectivity
 * This is for development/testing purposes only
 */
function ApiTest() {
  const [status, setStatus] = useState('');
  const [loading, setLoading] = useState(false);
  const [user, setUser] = useState(null);
  const [tasksList, setTasksList] = useState([]);

  const handleRegister = async () => {
    setLoading(true);
    setStatus('Registering...');
    try {
      const response = await auth.register(
        'webtest',
        'webtest@example.com',
        'TestPass123!'
      );
      setUser(response.user);
      setStatus(`✅ Registered as ${response.user.username}!`);
    } catch (error) {
      setStatus(`❌ Registration failed: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleLogin = async () => {
    setLoading(true);
    setStatus('Logging in...');
    try {
      const response = await auth.login('webtest', 'TestPass123!');
      setUser(response.user);
      setStatus(`✅ Logged in as ${response.user.username}!`);
    } catch (error) {
      setStatus(`❌ Login failed: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateTask = async () => {
    if (!user) {
      setStatus('❌ Please login first');
      return;
    }
    
    setLoading(true);
    setStatus('Creating task...');
    try {
      const newTask = await tasks.create({
        title: 'Test Task from Web',
        description: 'Testing API integration',
        priority: 3,
        category: 'Testing',
        due_date: '2025-10-20',
      });
      setStatus(`✅ Task created: ${newTask.title}`);
      handleGetTasks();
    } catch (error) {
      setStatus(`❌ Task creation failed: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleGetTasks = async () => {
    if (!user) {
      setStatus('❌ Please login first');
      return;
    }
    
    setLoading(true);
    setStatus('Fetching tasks...');
    try {
      const fetchedTasks = await tasks.list();
      setTasksList(fetchedTasks);
      setStatus(`✅ Found ${fetchedTasks.length} task(s)`);
    } catch (error) {
      setStatus(`❌ Failed to fetch tasks: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    auth.logout();
    setUser(null);
    setTasksList([]);
    setStatus('Logged out');
  };

  return (
    <div style={styles.container}>
      <h2>API Connection Test</h2>
      
      <div style={styles.userInfo}>
        {user ? (
          <div>
            <p>👤 Logged in as: <strong>{user.username}</strong></p>
            <p>📧 Email: {user.email}</p>
          </div>
        ) : (
          <p>Not logged in</p>
        )}
      </div>

      <div style={styles.buttonGroup}>
        <button onClick={handleRegister} disabled={loading || user} style={styles.button}>
          Register New User
        </button>
        <button onClick={handleLogin} disabled={loading || user} style={styles.button}>
          Login
        </button>
        <button onClick={handleLogout} disabled={loading || !user} style={styles.button}>
          Logout
        </button>
      </div>

      <div style={styles.buttonGroup}>
        <button onClick={handleCreateTask} disabled={loading || !user} style={styles.button}>
          Create Test Task
        </button>
        <button onClick={handleGetTasks} disabled={loading || !user} style={styles.button}>
          Get My Tasks
        </button>
      </div>

      {status && (
        <div style={styles.status}>
          {status}
        </div>
      )}

      {tasksList.length > 0 && (
        <div style={styles.tasksList}>
          <h3>Your Tasks:</h3>
          {tasksList.map(task => (
            <div key={task.id} style={styles.taskItem}>
              <strong>{task.title}</strong> - {task.priority_display}
              <br />
              <small>{task.description}</small>
              <br />
              <small>Status: {task.completed ? '✅ Complete' : '⏳ Incomplete'}</small>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

const styles = {
  container: {
    maxWidth: '600px',
    margin: '20px auto',
    padding: '20px',
    border: '1px solid #ddd',
    borderRadius: '8px',
    fontFamily: 'Arial, sans-serif',
  },
  userInfo: {
    backgroundColor: '#f0f0f0',
    padding: '15px',
    borderRadius: '5px',
    marginBottom: '20px',
  },
  buttonGroup: {
    display: 'flex',
    gap: '10px',
    marginBottom: '15px',
    flexWrap: 'wrap',
  },
  button: {
    padding: '10px 20px',
    fontSize: '14px',
    borderRadius: '5px',
    border: '1px solid #007bff',
    backgroundColor: '#007bff',
    color: 'white',
    cursor: 'pointer',
    transition: 'all 0.2s',
  },
  status: {
    padding: '15px',
    marginTop: '20px',
    backgroundColor: '#e9ecef',
    borderRadius: '5px',
    fontSize: '14px',
  },
  tasksList: {
    marginTop: '20px',
    padding: '15px',
    backgroundColor: '#f8f9fa',
    borderRadius: '5px',
  },
  taskItem: {
    padding: '10px',
    marginBottom: '10px',
    backgroundColor: 'white',
    borderRadius: '5px',
    border: '1px solid #dee2e6',
  },
};

export default ApiTest;
