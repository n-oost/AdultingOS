import React, { useEffect, useState } from 'react';
import './App.css';
import Chatbot from './components/Chatbot';
// import ApiTest from './components/ApiTest';
import LoginForm from './components/LoginForm';
import RegisterForm from './components/RegisterForm';
import TasksList from './components/TasksList';
import { setAuthToken, clearAuthToken } from './services/apiService';

/**
 * The main component of the AdultingOS application.
 */
function App() {
  // Track auth state and persist token for a smoother UX
  const [user, setUser] = useState(null);
  // Track which form to show: 'login' or 'register'
  const [showForm, setShowForm] = useState('login');

  useEffect(() => {
    // Load token from localStorage on boot (optional persistence)
    const savedToken = localStorage.getItem('authToken');
    const savedUser = localStorage.getItem('authUser');
    if (savedToken) setAuthToken(savedToken);
    if (savedUser) setUser(JSON.parse(savedUser));
  }, []);

  function handleLoginSuccess(u, token) {
    // Store token for API and persist to localStorage
    setAuthToken(token);
    localStorage.setItem('authToken', token);
    localStorage.setItem('authUser', JSON.stringify(u));
    setUser(u);
  }

  function handleRegisterSuccess(u, token) {
    // Store token for API and persist to localStorage
    setAuthToken(token);
    localStorage.setItem('authToken', token);
    localStorage.setItem('authUser', JSON.stringify(u));
    setUser(u);
  }

  function handleLogout() {
    clearAuthToken();
    localStorage.removeItem('authToken');
    localStorage.removeItem('authUser');
    setUser(null);
    setShowForm('login');
  }

  return (
    <div className="App">
      <h1 style={{ fontWeight: 700, fontSize: '2.2rem', marginBottom: 18, letterSpacing: '-1px' }}>AdultingOS</h1>

      {/* Auth gate: show login/register in a card until authenticated */}
      {!user ? (
        <div className="card">
          {showForm === 'login' ? (
            <>
              <div className="form-title">Sign In</div>
              <LoginForm onLoginSuccess={handleLoginSuccess} />
              <div className="form-actions" style={{ marginTop: 10 }}>
                <button className="btn btn-alt" onClick={() => setShowForm('register')}>
                  Need an account? Register
                </button>
              </div>
            </>
          ) : (
            <>
              <div className="form-title">Register</div>
              <RegisterForm onRegisterSuccess={handleRegisterSuccess} />
              <div className="form-actions" style={{ marginTop: 10 }}>
                <button className="btn btn-alt" onClick={() => setShowForm('login')}>
                  Already have an account? Login
                </button>
              </div>
            </>
          )}
        </div>
      ) : (
        <>
          <div className="card" style={{ marginBottom: 0 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 10 }}>
              <span style={{ fontSize: '1.05rem' }}>Signed in as <strong>{user.username}</strong></span>
              <button className="logout-btn" onClick={handleLogout}>Logout</button>
            </div>
            <TasksList />
          </div>

          <div className="card chatbot" style={{ marginTop: 24 }}>
            <h2 style={{ fontWeight: 600, fontSize: '1.3rem', marginBottom: 12 }}>Chatbot</h2>
            <Chatbot />
          </div>
        </>
      )}
    </div>
  );
}

export default App;