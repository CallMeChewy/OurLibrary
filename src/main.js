// Force rebuild timestamp: 2025-08-26 19:25  
import './styles.css';
import { render } from './router.js';

// Initialize the app
document.addEventListener('DOMContentLoaded', () => {
  // Set current year in footer
  const yearElement = document.getElementById('year');
  if (yearElement) {
    yearElement.textContent = new Date().getFullYear();
  }
  
  // Start the router
  render();
});