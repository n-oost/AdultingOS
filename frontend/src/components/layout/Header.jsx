/**
 * Header Component
 * 
 * Main navigation header with branding and user controls.
 * Responsive design with mobile menu support.
 */

import React, { useState } from 'react';
import './Header.css';

export default function Header({ user, onLogout, onThemeToggle, theme = 'light' }) {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const toggleMobileMenu = () => {
    setMobileMenuOpen(!mobileMenuOpen);
  };

  return (
    <header className="header">
      <div className="container">
        <div className="header__content">
          {/* Logo/Brand */}
          <div className="header__brand">
            <svg className="header__logo" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M12 2L2 7l10 5 10-5-10-5z"/>
              <path d="M2 17l10 5 10-5"/>
              <path d="M2 12l10 5 10-5"/>
            </svg>
            <h1 className="header__title">AdultingOS</h1>
          </div>

          {/* Desktop Navigation */}
          {user && (
            <nav className="header__nav" aria-label="Main navigation">
              <ul className="header__nav-list">
                <li><a href="#dashboard" className="header__nav-link header__nav-link--active">Dashboard</a></li>
                <li><a href="#tasks" className="header__nav-link">Tasks</a></li>
                <li><a href="#assistant" className="header__nav-link">Assistant</a></li>
              </ul>
            </nav>
          )}

          {/* User Controls */}
          <div className="header__actions">
            {/* Theme Toggle */}
            <button
              className="header__icon-btn"
              onClick={onThemeToggle}
              aria-label={`Switch to ${theme === 'light' ? 'dark' : 'light'} mode`}
              title={`Switch to ${theme === 'light' ? 'dark' : 'light'} mode`}
            >
              {theme === 'light' ? (
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
                </svg>
              ) : (
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <circle cx="12" cy="12" r="5"/>
                  <line x1="12" y1="1" x2="12" y2="3"/>
                  <line x1="12" y1="21" x2="12" y2="23"/>
                  <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/>
                  <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/>
                  <line x1="1" y1="12" x2="3" y2="12"/>
                  <line x1="21" y1="12" x2="23" y2="12"/>
                  <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/>
                  <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/>
                </svg>
              )}
            </button>

            {user && (
              <>
                {/* User Menu */}
                <div className="header__user">
                  <span className="header__username">{user.username}</span>
                  <button
                    className="header__logout-btn"
                    onClick={onLogout}
                    aria-label="Logout"
                  >
                    Logout
                  </button>
                </div>

                {/* Mobile Menu Toggle */}
                <button
                  className="header__mobile-toggle"
                  onClick={toggleMobileMenu}
                  aria-expanded={mobileMenuOpen}
                  aria-label="Toggle menu"
                >
                  {mobileMenuOpen ? (
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <line x1="18" y1="6" x2="6" y2="18"/>
                      <line x1="6" y1="6" x2="18" y2="18"/>
                    </svg>
                  ) : (
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <line x1="3" y1="12" x2="21" y2="12"/>
                      <line x1="3" y1="6" x2="21" y2="6"/>
                      <line x1="3" y1="18" x2="21" y2="18"/>
                    </svg>
                  )}
                </button>
              </>
            )}
          </div>
        </div>

        {/* Mobile Menu */}
        {user && mobileMenuOpen && (
          <nav className="header__mobile-nav" aria-label="Mobile navigation">
            <ul className="header__mobile-nav-list">
              <li>
                <a href="#dashboard" className="header__mobile-nav-link header__mobile-nav-link--active">
                  Dashboard
                </a>
              </li>
              <li>
                <a href="#tasks" className="header__mobile-nav-link">
                  Tasks
                </a>
              </li>
              <li>
                <a href="#assistant" className="header__mobile-nav-link">
                  Assistant
                </a>
              </li>
            </ul>
          </nav>
        )}
      </div>
    </header>
  );
}
