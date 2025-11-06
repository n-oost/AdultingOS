/**
 * Card Component
 * 
 * A versatile card container with multiple variants for different use cases.
 * Supports hover states and clickable cards.
 */

import React from 'react';
import './Card.css';

/**
 * @param {Object} props
 * @param {'default' | 'elevated' | 'outlined' | 'flat'} props.variant - Card style
 * @param {boolean} props.hoverable - Add hover effect
 * @param {boolean} props.clickable - Make card clickable
 * @param {Function} props.onClick - Click handler
 * @param {string} props.className - Additional CSS classes
 * @param {React.ReactNode} props.children - Card content
 */
export default function Card({
  variant = 'default',
  hoverable = false,
  clickable = false,
  onClick,
  className = '',
  children,
  as: Component = 'div',
  ...props
}) {
  // Only make clickable if onClick is provided
  const isClickable = clickable && onClick;
  
  const classes = [
    'card',
    `card--${variant}`,
    (hoverable || onClick) && 'card--hoverable',
    isClickable && 'card--clickable',
    className
  ].filter(Boolean).join(' ');

  const handleKeyDown = isClickable ? (e) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      onClick?.(e);
    }
  } : undefined;

  return (
    <Component
      className={classes}
      onClick={onClick}
      onKeyDown={handleKeyDown}
      tabIndex={isClickable ? 0 : undefined}
      role={isClickable ? 'button' : undefined}
      {...props}
    >
      {children}
    </Component>
  );
}

/**
 * CardHeader - Header section of a card
 */
export function CardHeader({ children, className = '', ...props }) {
  return (
    <div className={`card__header ${className}`} {...props}>
      {children}
    </div>
  );
}

/**
 * CardBody - Main content section of a card
 */
export function CardBody({ children, className = '', ...props }) {
  return (
    <div className={`card__body ${className}`} {...props}>
      {children}
    </div>
  );
}

/**
 * CardFooter - Footer section of a card
 */
export function CardFooter({ children, className = '', ...props }) {
  return (
    <div className={`card__footer ${className}`} {...props}>
      {children}
    </div>
  );
}
