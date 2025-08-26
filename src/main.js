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