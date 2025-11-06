import React, { useEffect, useState } from 'react';
import './App.css';
import Header from './components/layout/Header';
import Dashboard from './components/Dashboard';
import Chatbot from './components/Chatbot';
import LoginForm from './components/LoginForm';
import RegisterForm from './components/RegisterForm';
import TasksList from './components/TasksList';
import Card, { CardHeader, CardBody } from './ui/Card';
import Button from './ui/Button';
import { setAuthToken, clearAuthToken } from './services/apiService';

/**
 * The main component of the AdultingOS application.
 */
function App() {
  // Track auth state and persist token for a smoother UX
  const [user, setUser] = useState(null);
  // Track which form to show: 'login' or 'register'
  const [showForm, setShowForm] = useState('login');
  // Track current view: 'dashboard', 'tasks', 'assistant'
  const [currentView, setCurrentView] = useState('dashboard');
  // Track theme
  const [theme, setTheme] = useState(() => {
    const savedTheme = localStorage.getItem('theme');
    return savedTheme || 'light';
  });

  useEffect(() => {
    // Load token from localStorage on boot (optional persistence)
    const savedToken = localStorage.getItem('authToken');
    const savedUser = localStorage.getItem('authUser');
    if (savedToken) setAuthToken(savedToken);
    if (savedUser) setUser(JSON.parse(savedUser));
  }, []);

  useEffect(() => {
    // Apply theme to document
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
  }, [theme]);

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
    setCurrentView('dashboard');
  }

  function toggleTheme() {
    setTheme(prevTheme => prevTheme === 'light' ? 'dark' : 'light');
  }

  return (
    <div className="App">
      {user && (
        <Header 
          user={user} 
          onLogout={handleLogout} 
          onThemeToggle={toggleTheme}
          theme={theme}
        />
      )}

      <main className="App__main">
        <div className="container">
          {/* Auth gate: show login/register in a card until authenticated */}
          {!user ? (
            <div className="auth-container">
              <div className="auth-card">
                <div className="auth-card__brand">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M12 2L2 7l10 5 10-5-10-5z"/>
                    <path d="M2 17l10 5 10-5"/>
                    <path d="M2 12l10 5 10-5"/>
                  </svg>
                  <h1>AdultingOS</h1>
                </div>
                
                <Card variant="elevated">
                  <CardHeader>
                    <h2 className="auth-card__title">
                      {showForm === 'login' ? 'Welcome back' : 'Create your account'}
                    </h2>
                    <p className="auth-card__subtitle">
                      {showForm === 'login' 
                        ? 'Sign in to continue to your dashboard' 
                        : 'Get started with AdultingOS today'}
                    </p>
                  </CardHeader>
                  <CardBody>
                    {showForm === 'login' ? (
                      <LoginForm onLoginSuccess={handleLoginSuccess} />
                    ) : (
                      <RegisterForm onRegisterSuccess={handleRegisterSuccess} />
                    )}
                  </CardBody>
                </Card>

                <div className="auth-card__switch">
                  {showForm === 'login' ? (
                    <>
                      <span>Don't have an account?</span>
                      <Button variant="ghost" onClick={() => setShowForm('register')}>
                        Sign up
                      </Button>
                    </>
                  ) : (
                    <>
                      <span>Already have an account?</span>
                      <Button variant="ghost" onClick={() => setShowForm('login')}>
                        Sign in
                      </Button>
                    </>
                  )}
                </div>
              </div>
            </div>
          ) : (
            <>
              {/* Render current view based on navigation */}
              {currentView === 'dashboard' && <Dashboard user={user} />}
              
              {currentView === 'tasks' && (
                <div className="content-section">
                  <h2 className="content-section__title">My Tasks</h2>
                  <Card variant="default">
                    <CardBody>
                      <TasksList />
                    </CardBody>
                  </Card>
                </div>
              )}
              
              {currentView === 'assistant' && (
                <div className="content-section">
                  <h2 className="content-section__title">AI Assistant</h2>
                  <Card variant="default">
                    <CardBody>
                      <Chatbot />
                    </CardBody>
                  </Card>
                </div>
              )}
            </>
          )}
        </div>
      </main>
    </div>
  );
}

export default App;