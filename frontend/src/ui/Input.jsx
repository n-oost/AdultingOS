/**
 * Input Component
 * 
 * A flexible, accessible input component with validation states.
 * Supports labels, helper text, and error messages.
 */

import React from 'react';
import './Input.css';

/**
 * @param {Object} props
 * @param {string} props.label - Input label
 * @param {string} props.type - Input type
 * @param {string} props.error - Error message
 * @param {string} props.helperText - Helper text below input
 * @param {boolean} props.required - Mark as required
 * @param {boolean} props.disabled - Disable input
 * @param {string} props.placeholder - Placeholder text
 * @param {React.ReactNode} props.leftIcon - Icon before input
 * @param {React.ReactNode} props.rightIcon - Icon after input
 */
export default function Input({
  label,
  type = 'text',
  error,
  helperText,
  required = false,
  disabled = false,
  placeholder,
  leftIcon,
  rightIcon,
  className = '',
  id,
  ...props
}) {
  const inputId = id || `input-${Math.random().toString(36).substr(2, 9)}`;
  const hasError = Boolean(error);

  const inputClasses = [
    'input__field',
    leftIcon && 'input__field--with-left-icon',
    rightIcon && 'input__field--with-right-icon',
    hasError && 'input__field--error',
    disabled && 'input__field--disabled'
  ].filter(Boolean).join(' ');

  return (
    <div className={`input ${className}`}>
      {label && (
        <label htmlFor={inputId} className="input__label">
          {label}
          {required && <span className="input__required" aria-label="required"> *</span>}
        </label>
      )}
      
      <div className="input__wrapper">
        {leftIcon && (
          <span className="input__icon input__icon--left" aria-hidden="true">
            {leftIcon}
          </span>
        )}
        
        <input
          id={inputId}
          type={type}
          className={inputClasses}
          placeholder={placeholder}
          disabled={disabled}
          required={required}
          aria-invalid={hasError}
          aria-describedby={
            hasError ? `${inputId}-error` : helperText ? `${inputId}-helper` : undefined
          }
          {...props}
        />
        
        {rightIcon && (
          <span className="input__icon input__icon--right" aria-hidden="true">
            {rightIcon}
          </span>
        )}
      </div>
      
      {error && (
        <p id={`${inputId}-error`} className="input__error" role="alert">
          {error}
        </p>
      )}
      
      {!error && helperText && (
        <p id={`${inputId}-helper`} className="input__helper">
          {helperText}
        </p>
      )}
    </div>
  );
}
