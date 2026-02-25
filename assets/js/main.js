(function () {
  const header = document.querySelector('.site-header');
  const navToggle = document.querySelector('.nav-toggle');

  if (header && navToggle) {
    navToggle.addEventListener('click', () => {
      const expanded = navToggle.getAttribute('aria-expanded') === 'true';
      navToggle.setAttribute('aria-expanded', String(!expanded));
      header.classList.toggle('nav-open', !expanded);
    });
  }

  document.addEventListener('click', (e) => {
    const a = e.target.closest('a[href^="#"]');
    if (!a) return;
    const target = a.getAttribute('href');
    if (!target || target === '#') return;
    const node = document.querySelector(target);
    if (!node) return;
    e.preventDefault();
    node.scrollIntoView({ behavior: 'smooth' });
  });
})();
