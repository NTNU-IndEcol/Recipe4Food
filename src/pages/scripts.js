// scripts.js
document.addEventListener('DOMContentLoaded', () => {
    const navToggle = document.querySelector('.nav-toggle');
    const navLinks = document.querySelector('nav ul');
  
    navToggle.addEventListener('click', () => {
      navLinks.classList.toggle('show-nav');
    });
  });
  