# AdultingOS UI Design System

## Overview

This document describes the modern, banking-inspired UI design system implemented for AdultingOS. The design prioritizes clarity, accessibility, and a premium user experience while maintaining consistency across all components.

## Design Philosophy

- **Clean & Modern**: Inspired by premium banking apps with generous whitespace and clear visual hierarchy
- **Accessible**: WCAG AA compliant with keyboard navigation and screen reader support
- **Responsive**: Mobile-first design that adapts seamlessly to all screen sizes
- **Performant**: Subtle micro-interactions (100-200ms) that enhance UX without sacrificing performance
- **Themeable**: Built-in light and dark mode support

## Design Tokens

All design tokens are defined in `/src/design-tokens.css` using CSS custom properties.

### Color System

#### Primary Brand Colors
- Used for primary actions, links, and brand elements
- Range: `--color-primary-50` to `--color-primary-900`
- Main color: `--color-primary-600` (#2563eb)

#### Neutral Colors
- Used for text, backgrounds, and borders
- Range: `--color-neutral-0` (white) to `--color-neutral-950` (near black)

#### Semantic Colors
- **Success**: Green shades for positive actions and confirmations
- **Warning**: Amber shades for cautions and alerts
- **Error**: Red shades for errors and destructive actions
- **Info**: Blue shades for informational messages

### Typography

**Font Family**
```css
--font-sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Helvetica Neue', Arial, sans-serif;
```

**Font Sizes**
- `--text-xs`: 0.75rem (12px)
- `--text-sm`: 0.875rem (14px)
- `--text-base`: 1rem (16px)
- `--text-lg`: 1.125rem (18px)
- `--text-xl`: 1.25rem (20px)
- `--text-2xl`: 1.5rem (24px)
- `--text-3xl`: 1.875rem (30px)
- `--text-4xl`: 2.25rem (36px)

**Font Weights**
- Normal: 400
- Medium: 500
- Semibold: 600
- Bold: 700

### Spacing

Based on a 4px grid system:
- `--space-1`: 0.25rem (4px)
- `--space-2`: 0.5rem (8px)
- `--space-3`: 0.75rem (12px)
- `--space-4`: 1rem (16px)
- `--space-5`: 1.25rem (20px)
- `--space-6`: 1.5rem (24px)
- `--space-8`: 2rem (32px)
- `--space-10`: 2.5rem (40px)
- `--space-12`: 3rem (48px)
- `--space-16`: 4rem (64px)
- `--space-20`: 5rem (80px)
- `--space-24`: 6rem (96px)

### Border Radius

- `--radius-sm`: 0.25rem (4px)
- `--radius-md`: 0.375rem (6px)
- `--radius-lg`: 0.5rem (8px)
- `--radius-xl`: 0.75rem (12px)
- `--radius-2xl`: 1rem (16px)
- `--radius-full`: 9999px (pill shape)

### Shadows

Progressive elevation system:
- `--shadow-xs`: Minimal elevation
- `--shadow-sm`: Subtle elevation
- `--shadow-md`: Standard elevation
- `--shadow-lg`: Prominent elevation
- `--shadow-xl`: High elevation
- `--shadow-2xl`: Maximum elevation

### Animations

**Duration**
- `--duration-fast`: 100ms
- `--duration-normal`: 150ms
- `--duration-slow`: 200ms

**Easing**
- `--ease-in`: cubic-bezier(0.4, 0, 1, 1)
- `--ease-out`: cubic-bezier(0, 0, 0.2, 1)
- `--ease-in-out`: cubic-bezier(0.4, 0, 0.2, 1)

## Component Library

### Button

A flexible button component with multiple variants and states.

**Import**
```jsx
import Button from './ui/Button';
```

**Variants**
- `primary`: Main call-to-action (blue background)
- `secondary`: Alternative action (white background with border)
- `outline`: Subtle action (transparent with border)
- `ghost`: Minimal style (transparent, no border)
- `destructive`: Danger action (red background)

**Sizes**
- `sm`: 36px height
- `md`: 44px height (default)
- `lg`: 52px height

**Example Usage**
```jsx
<Button variant="primary" size="lg">
  Create Task
</Button>

<Button variant="secondary" onClick={handleCancel}>
  Cancel
</Button>

<Button variant="destructive" loading={isDeleting}>
  Delete
</Button>

<Button variant="ghost" leftIcon={<IconComponent />}>
  Settings
</Button>
```

**Props**
- `variant`: Visual style (default: 'primary')
- `size`: Button size (default: 'md')
- `fullWidth`: Take full width of container
- `loading`: Show loading spinner
- `disabled`: Disable button
- `leftIcon`: Icon before text
- `rightIcon`: Icon after text

### Input

An input component with validation states and icon support.

**Import**
```jsx
import Input from './ui/Input';
```

**Example Usage**
```jsx
<Input
  label="Email"
  type="email"
  placeholder="Enter your email"
  value={email}
  onChange={(e) => setEmail(e.target.value)}
  required
  leftIcon={<MailIcon />}
/>

<Input
  label="Password"
  type="password"
  error="Password is too short"
  helperText="Must be at least 8 characters"
/>
```

**Props**
- `label`: Input label text
- `type`: Input type (default: 'text')
- `error`: Error message to display
- `helperText`: Helper text below input
- `required`: Mark as required field
- `disabled`: Disable input
- `leftIcon`: Icon before input
- `rightIcon`: Icon after input

### Card

A versatile card container for grouping content.

**Import**
```jsx
import Card, { CardHeader, CardBody, CardFooter } from './ui/Card';
```

**Variants**
- `default`: Standard card with border and subtle shadow
- `elevated`: Prominent shadow
- `outlined`: Bold border
- `flat`: No border or shadow

**Example Usage**
```jsx
<Card variant="elevated">
  <CardHeader>
    <h3>Dashboard</h3>
  </CardHeader>
  <CardBody>
    <p>Your content here</p>
  </CardBody>
  <CardFooter>
    <Button>Action</Button>
  </CardFooter>
</Card>

<Card hoverable clickable onClick={handleClick}>
  <CardBody>
    Clickable card with hover effect
  </CardBody>
</Card>
```

**Props**
- `variant`: Visual style (default: 'default')
- `hoverable`: Add hover effect
- `clickable`: Make card clickable
- `onClick`: Click handler

## Layout Components

### Header

Sticky navigation header with branding, navigation links, and user controls.

**Features**
- Responsive mobile menu
- Theme toggle (light/dark mode)
- User profile display
- Logout button

**Import**
```jsx
import Header from './components/layout/Header';
```

**Usage**
```jsx
<Header 
  user={user} 
  onLogout={handleLogout}
  onThemeToggle={toggleTheme}
  theme={theme}
/>
```

### Dashboard

Main dashboard view with stats cards and recent activity.

**Features**
- Summary statistics cards
- Quick action buttons
- Recent tasks list
- Responsive grid layout

**Import**
```jsx
import Dashboard from './components/Dashboard';
```

## Theming

### Light/Dark Mode

The design system supports both light and dark themes. Theme is controlled via the `data-theme` attribute on the document root.

**Setting Theme**
```jsx
// Light mode (default)
document.documentElement.setAttribute('data-theme', 'light');

// Dark mode
document.documentElement.setAttribute('data-theme', 'dark');
```

**Persistence**
```jsx
// Save theme preference
localStorage.setItem('theme', theme);

// Load theme preference
const savedTheme = localStorage.getItem('theme') || 'light';
document.documentElement.setAttribute('data-theme', savedTheme);
```

## Accessibility

### Keyboard Navigation

All interactive elements are keyboard accessible:
- Tab order follows visual flow
- Focus states clearly visible
- Enter/Space activate buttons
- Escape closes modals

### Focus Indicators

All focusable elements have clear focus indicators:
```css
:focus-visible {
  outline: 2px solid var(--border-focus);
  outline-offset: 2px;
}
```

### ARIA Attributes

Components include appropriate ARIA attributes:
- `aria-label` for icon-only buttons
- `aria-describedby` for form field descriptions
- `aria-invalid` for error states
- `role="alert"` for error messages

### Color Contrast

All text meets WCAG AA standards:
- Body text: >= 4.5:1 contrast ratio
- Large text: >= 3:1 contrast ratio
- Interactive elements: >= 3:1 contrast ratio

### Screen Readers

- Semantic HTML elements used throughout
- Hidden labels for icon buttons
- Status messages announced via `role="alert"`
- Loading states indicated with `aria-busy`

## Responsive Design

### Breakpoints

```css
/* Mobile first approach */
@media (min-width: 640px) { /* sm */ }
@media (min-width: 768px) { /* md */ }
@media (min-width: 1024px) { /* lg */ }
@media (min-width: 1280px) { /* xl */ }
```

### Mobile Optimizations

- Touch-friendly target sizes (minimum 44x44px)
- Simplified navigation via hamburger menu
- Stacked layouts on small screens
- Larger font sizes for better readability

## Best Practices

### Using Design Tokens

Always use design tokens instead of hard-coded values:

```css
/* ✅ Good */
.my-component {
  padding: var(--space-4);
  color: var(--text-primary);
  border-radius: var(--radius-lg);
}

/* ❌ Bad */
.my-component {
  padding: 16px;
  color: #171717;
  border-radius: 8px;
}
```

### Animation Performance

- Use CSS transforms for animations
- Prefer `opacity` and `transform` over `width`/`height`
- Keep durations under 200ms for micro-interactions
- Respect `prefers-reduced-motion` setting

### Component Composition

Build complex UIs by composing simple components:

```jsx
<Card variant="elevated">
  <CardBody>
    <Input 
      label="Email"
      leftIcon={<MailIcon />}
    />
    <Button variant="primary" fullWidth>
      Submit
    </Button>
  </CardBody>
</Card>
```

## File Structure

```
frontend/src/
├── design-tokens.css       # Design system tokens
├── global.css              # Global styles and resets
├── ui/                     # Reusable UI components
│   ├── Button.jsx
│   ├── Button.css
│   ├── Input.jsx
│   ├── Input.css
│   ├── Card.jsx
│   ├── Card.css
│   └── index.js            # Component exports
├── components/             # Feature components
│   ├── layout/
│   │   ├── Header.jsx
│   │   └── Header.css
│   ├── Dashboard.jsx
│   ├── Dashboard.css
│   ├── LoginForm.jsx
│   ├── RegisterForm.jsx
│   └── AuthForms.css
└── App.js                  # Main app component
```

## Development

### Running the App

```bash
cd frontend
npm install
npm start
```

App will be available at http://localhost:3000

### Building for Production

```bash
npm run build
```

### Running Tests

```bash
npm test
```

## Browser Support

- Chrome (last 2 versions)
- Firefox (last 2 versions)
- Safari (last 2 versions)
- Edge (last 2 versions)
- Mobile browsers (iOS Safari, Chrome Mobile)

## Future Enhancements

Potential additions to the design system:

- Modal/Dialog component
- Toast notification system
- Badge component
- Loading skeleton screens
- Dropdown menu component
- Tabs component
- Progress indicators
- Storybook documentation
- Visual regression tests

## Resources

- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [Material Design Accessibility](https://material.io/design/usability/accessibility.html)
- [CSS Custom Properties](https://developer.mozilla.org/en-US/docs/Web/CSS/Using_CSS_custom_properties)
- [React Accessibility](https://reactjs.org/docs/accessibility.html)
