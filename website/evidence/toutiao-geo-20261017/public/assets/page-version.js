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
  // Only known service pages inside this language/site can own a case return.
  function serviceSource(url, prefix) {
    const slugs=['fde-consulting','ai-agent','workflow-automation'];
    if (url.origin!==location.origin || !slugs.some(slug=>url.pathname===prefix+'services/'+slug+'.html')) return null;
    const clean=new URL(url.pathname,location.origin);
    clean.hash=['#cases','#service-proof'].includes(url.hash) ? url.hash : '#cases';
    clean.searchParams.set('pv',revision);
    return clean;
  }
  function homeSource(url, prefix, project) {
    if (url.origin!==location.origin || ![prefix,prefix+'index.html'].includes(url.pathname)) return null;
    const clean=new URL(url.pathname,location.origin);
    const selected=url.searchParams.get('project') || project;
    if (/^(p\d{2}|n\d{2})$/.test(selected || '')) clean.searchParams.set('project',selected);
    clean.searchParams.set('pv',revision);
    clean.hash='#work';
    return clean;
  }
  // Return context belongs to navigation, independently of animation startup.
  // The origin row stays the same while the reader follows related cases.
  function restoreCaseOrigin() {
    if (!location.pathname.includes('/cases/')) return;
    const back=document.querySelector('.back');
    const title=document.querySelector('.detail-header [data-project-title]');
    if (!back?.href || !title?.dataset?.projectTitle) return;
    try {
      const prefix=location.pathname.slice(0,location.pathname.lastIndexOf('/cases/')+1);
      const expected=new URL(prefix+'records.html',location.origin);
      let origin=new URL(location.href).searchParams.get('from') || history.state?.eliProjectReturnSource;
      const referrer=document.referrer ? new URL(document.referrer) : null;
      if (!origin && referrer && serviceSource(referrer,prefix)) origin=referrer.href;
      if (!origin && referrer && homeSource(referrer,prefix)) origin=referrer.href;
      if (!origin && referrer?.origin===location.origin && referrer.pathname===expected.pathname) {
        const saved=JSON.parse(sessionStorage.getItem('eli-project-return') || 'null');
        if (saved?.id===title.dataset.projectTitle.toLowerCase()) {
          const previous=new URL(saved.source,location.origin);
          // Older links without `from` may use their real list referrer, but
          // never a session left over before the reader cleared/changed it.
          const actualList=new URL(referrer);
          for (const url of [previous,actualList]) {
            url.searchParams.delete('pv');url.searchParams.delete('return');
            url.searchParams.sort();url.hash='';
          }
          if (previous.href===actualList.href) {
            previous.searchParams.set('return',saved.id);
            origin=previous.pathname+previous.search;
          }
        }
      }
      const supplied=origin ? new URL(origin,location.origin) : null;
      if (!supplied || supplied.origin!==location.origin) return;
      const fromService=serviceSource(supplied,prefix);
      const fromHome=homeSource(supplied,prefix,title.dataset.projectTitle.toLowerCase());
      const source=fromService || fromHome || (supplied.pathname===expected.pathname &&
        /^(p\d{2}|n\d{2})$/.test(supplied.searchParams.get('return') || '') ? supplied : null);
      if (!source) return;
      source.searchParams.set('pv',revision);
      back.href=source.pathname+source.search;
      if (fromService || fromHome) {
        back.href+=source.hash;
        back.textContent=fromHome
          ? (document.documentElement?.lang==='en' ? '← Back to homepage projects' : '← 返回首页案例')
          : (document.documentElement?.lang==='en' ? '← Back to service' : '← 返回服务介绍');
      }
      history.replaceState({...history.state,eliProjectReturnSource:back.href},'');
      document.querySelectorAll('.case-related a').forEach(link=> {
        const destination=new URL(link.href,location.href);
        if (!internal(destination)) return;
        destination.searchParams.set('from',source.pathname+source.search+source.hash);
        link.href=destination.pathname+destination.search+destination.hash;
      });
    } catch (_) {}
  }
  function rememberCaseOrigin(link) {
    const homePrefix=location.pathname.endsWith('/index.html')
      ? location.pathname.slice(0,-'index.html'.length)
      : location.pathname.endsWith('/') ? location.pathname : null;
    if (homePrefix) {
      const destination=new URL(link.href,location.href);
      const id=destination.pathname.match(/\/cases\/((?:p\d{2}|n\d{2}))\.html$/)?.[1];
      if (!id || !internal(destination) || destination.pathname!==homePrefix+'cases/'+id+'.html') return;
      const home=homeSource(new URL(location.href),homePrefix,id);
      // A newly selected card owns this return, even after an earlier return URL.
      home.searchParams.set('project',id);
      destination.searchParams.set('from',home.pathname+home.search+home.hash);
      link.href=destination.pathname+destination.search;
      return;
    }
    const prefix=location.pathname.slice(0,location.pathname.lastIndexOf('/services/')+1);
    const service=serviceSource(new URL(location.href),prefix);
    if (service) {
      const destination=new URL(link.href,location.href);
      if (!internal(destination) || !destination.pathname.startsWith(prefix+'cases/') ||
          !/\/cases\/(?:p\d{2}|n\d{2})\.html$/.test(destination.pathname)) return;
      service.hash=link.closest('#service-proof') ? '#service-proof' : '#cases';
      destination.searchParams.set('from',service.pathname+service.search+service.hash);
      link.href=destination.pathname+destination.search+destination.hash;
      return;
    }
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
    if (link) { rememberCaseOrigin(link); stampLink(link); }
  }, {capture:true});
})();
