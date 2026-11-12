/* Reuse the existing disclosure animation; native details remain the fallback. */
(() => {
  'use strict';
  document.querySelectorAll('[data-industry]').forEach(details => {
    const summary = details.querySelector('summary');
    summary.addEventListener('click', event => {
      if (!window.PortfolioMotion?.toggleDetails) return;
      event.preventDefault();
      window.PortfolioMotion.toggleDetails(details, () => {});
    });
  });
})();
