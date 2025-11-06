/**
 * Button Component
 * 
 * A flexible, accessible button component with multiple variants and sizes.
 * Follows banking app design patterns with clear visual hierarchy.
 */

import React from 'react';
import './Button.css';

/**
 * @param {Object} props
 * @param {'primary' | 'secondary' | 'outline' | 'ghost' | 'destructive'} props.variant - Visual style
 * @param {'sm' | 'md' | 'lg'} props.size - Button size
 * @param {boolean} props.fullWidth - Whether button takes full width
 * @param {boolean} props.loading - Show loading state
 * @param {boolean} props.disabled - Disable button
 * @param {string} props.className - Additional CSS classes
 * @param {React.ReactNode} props.children - Button content
 * @param {React.ReactNode} props.leftIcon - Icon before text
 * @param {React.ReactNode} props.rightIcon - Icon after text
 */
export default function Button({
  variant = 'primary',
  size = 'md',
  fullWidth = false,
  loading = false,
  disabled = false,
  className = '',
  children,
  leftIcon,
  rightIcon,
  type = 'button',
  ...props
}) {
  const classes = [
    'btn',
    `btn--${variant}`,
    `btn--${size}`,
    fullWidth && 'btn--full-width',
    loading && 'btn--loading',
    className
  ].filter(Boolean).join(' ');

  return (
    <button
      type={type}
      className={classes}
      disabled={disabled || loading}
      aria-busy={loading}
      {...props}
    >
      {loading && (
        <span className="btn__spinner" aria-label="Loading">
          <svg className="btn__spinner-icon" viewBox="0 0 24 24">
            <circle
              className="btn__spinner-circle"
              cx="12"
              cy="12"
              r="10"
              fill="none"
              strokeWidth="3"
            />
          </svg>
        </span>
      )}
      {!loading && leftIcon && <span className="btn__icon-left">{leftIcon}</span>}
      <span className="btn__text">{children}</span>
      {!loading && rightIcon && <span className="btn__icon-right">{rightIcon}</span>}
    </button>
  );
}
