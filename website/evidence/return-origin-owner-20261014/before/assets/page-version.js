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
  // Return context belongs to navigation, independently of animation startup.
  // The origin row stays the same while the reader follows related cases.
  function restoreCaseOrigin() {
    if (!location.pathname.includes('/cases/')) return;
    const back=document.querySelector('.back');
    const title=document.querySelector('.detail-header [data-project-title]');
    if (!back?.href || !title?.dataset?.projectTitle) return;
    try {
      const expected=new URL(back.href,location.href);
      let origin=new URL(location.href).searchParams.get('from') || history.state?.eliProjectReturnSource;
      if (!origin && document.referrer && new URL(document.referrer).pathname===expected.pathname) {
        const saved=JSON.parse(sessionStorage.getItem('eli-project-return') || 'null');
        if (saved?.id===title.dataset.projectTitle.toLowerCase()) {
          const previous=new URL(saved.source,location.origin);
          previous.searchParams.set('return',saved.id);
          origin=previous.pathname+previous.search;
        }
      }
      const source=origin ? new URL(origin,location.origin) : null;
      if (!source || source.origin!==location.origin || source.pathname!==expected.pathname ||
          !/^(p\d{2}|n\d{2})$/.test(source.searchParams.get('return') || '')) return;
      source.searchParams.set('pv',revision);
      back.href=source.pathname+source.search;
      history.replaceState({...history.state,eliProjectReturnSource:back.href},'');
      document.querySelectorAll('.case-related a').forEach(link=> {
        const destination=new URL(link.href,location.href);
        if (!internal(destination)) return;
        destination.searchParams.set('from',source.pathname+source.search);
        link.href=destination.pathname+destination.search+destination.hash;
      });
    } catch (_) {}
  }
  function rememberListOrigin(link) {
    if (!location.pathname.endsWith('/records.html')) return;
    const row=link.closest('.archive-list li');
    const title=row?.querySelector('[data-project-title]');
    if (!title) return;
    const id=title.dataset.projectTitle.toLowerCase();
    const origin=new URL(location.href);
    origin.searchParams.set('return',id);
    const destination=new URL(link.href,location.href);
    if (!internal(destination)) return;
    destination.searchParams.set('from',origin.pathname+origin.search);
    link.href=destination.pathname+destination.search;
    try {sessionStorage.setItem('eli-project-return',JSON.stringify({
      source:location.pathname+location.search,scroll:scrollY,id
    }));} catch (_) {}
  }
  function stampPage() {
    const url = versionURL(location.href);
    if (internal(url) && url.href !== location.href) {
      // Replace only this address: no extra Back step and no lost reading state.
      history.replaceState(history.state, '', url.pathname + url.search + url.hash);
    }
    restoreCaseOrigin();
    document.querySelectorAll('a[href]').forEach(stampLink);
  }
  stampPage();
  addEventListener('pageshow', stampPage);
  // Also covers return links adjusted later by the existing reading controller.
  document.addEventListener('click', event => {
    const link = event.target.closest?.('a[href]');
    if (link) { rememberListOrigin(link); stampLink(link); }
  }, {capture:true});
})();
