import { render, screen } from '@testing-library/react';
import App from './App';

test('renders AdultingOS branding', () => {
  render(<App />);
  const brandElement = screen.getByText(/AdultingOS/i);
  expect(brandElement).toBeInTheDocument();
});

test('renders login form when not authenticated', () => {
  render(<App />);
  const welcomeText = screen.getByText(/Welcome back/i);
  expect(welcomeText).toBeInTheDocument();
  
  const usernameInput = screen.getByLabelText(/Username/i);
  expect(usernameInput).toBeInTheDocument();
  
  const passwordInput = screen.getByLabelText(/Password/i);
  expect(passwordInput).toBeInTheDocument();
});
