// Simple DOM utilities
export const $ = (selector) => document.querySelector(selector);

export const mount = (html) => {
  const view = document.getElementById('view');
  if (view) view.innerHTML = html;
};

export const withForm = (selector, handler) => {
  const form = $(selector);
  if (!form) return;
  
  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const formData = new FormData(form);
    const data = Object.fromEntries(formData);
    
    // Handle checkboxes
    form.querySelectorAll('input[type="checkbox"]').forEach(cb => {
      if (cb.checked) data[cb.name] = cb.value || 'on';
    });
    
    try {
      await handler(data);
    } catch (err) {
      console.error('Form handler error:', err);
    }
  });
};