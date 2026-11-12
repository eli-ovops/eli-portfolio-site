(() => {
  'use strict';
  const revision = document.querySelector('meta[name="portfolio-revision"]')?.content;
  const script = document.currentScript;
  if (!/^[a-f0-9]{20}$/.test(revision || '') || !script?.src) return;
  const base = new URL('../', script.src);
  const internal = url => url.origin === base.origin && url.pathname.startsWith(base.pathname)
    && (url.pathname.endsWith('.html') || url.pathname === base.pathname);
  function versionURL(value) {
    const url = new URL(value, location.href);
    if (internal(url)) url.searchParams.set('pv', revision);
    return url;
  }
  function stampLink(link) {
    const url = versionURL(link.href);
    if (internal(url) && link.href !== url.href) link.href = url.pathname + url.search + url.hash;
  }
  function stampPage() {
    const url = versionURL(location.href);
    if (internal(url) && url.href !== location.href) {
      // Replace only this address: no extra Back step and no lost reading state.
      history.replaceState(history.state, '', url.pathname + url.search + url.hash);
    }
    document.querySelectorAll('a[href]').forEach(stampLink);
  }
  stampPage();
  addEventListener('pageshow', stampPage);
  // Also covers return links adjusted later by the existing reading controller.
  document.addEventListener('click', event => {
    const link = event.target.closest?.('a[href]');
    if (link) stampLink(link);
  }, {capture:true});
})();
