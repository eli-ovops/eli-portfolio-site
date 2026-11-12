(() => {
  'use strict';
  const ownScript = document.currentScript;
  const site = ownScript?.dataset.baiduSite;
  const canonical = document.querySelector('link[rel="canonical"]')?.href;
  // Explicit loopback preview shows only the consent UI, never the collector.
  const localPreview = location.hostname === '127.0.0.1' &&
    new URL(location.href).searchParams.get('analytics-preview') === '1';
  if ((location.origin !== 'https://www.eliai.cn' && !localPreview) || !/^[a-f0-9]{32}$/.test(site || '') || !canonical) return;
  const page = new URL(canonical);
  if (page.origin !== 'https://www.eliai.cn' || document.documentElement.dataset.eliAnalytics) return;
  document.documentElement.dataset.eliAnalytics = 'ready';
  const root = document.documentElement;
  const key = 'eli-analytics-consent-' + ownScript.dataset.consentVersion;
  const notice = document.getElementById('analytics-notice');
  const dialog = document.getElementById('analytics-dialog');
  let choice;
  if (!localPreview) { try { choice = localStorage.getItem(key); } catch (_) {} }
  let started = false;
  let closing = false;
  function reserveSpace() {
    const visible = notice && !notice.hidden;
    root.classList.toggle('analytics-notice-active', !!visible);
    root.style.setProperty('--analytics-notice-space', visible ? Math.ceil(notice.getBoundingClientRect().height) + 'px' : '0px');
  }
  function hideNotice(after) {
    const finish = () => { if (notice) notice.hidden = true; closing = false; reserveSpace(); after?.(); };
    const reduceMotion = typeof matchMedia === 'function' && matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (notice && !notice.hidden && notice.animate && !reduceMotion) {
      closing = true;
      const animation = notice.animate([{opacity:1,transform:'translateY(0)'},{opacity:0,transform:'translateY(12px)'}],
        {duration:200,easing:'ease-in',fill:'forwards'});
      animation.finished.then(() => { finish(); animation.cancel(); }, finish);
    } else finish();
  }
  const queue = value => { if (started && choice === 'allow') window._hmt.push(value); };
  function start() {
    if (started || localPreview) return;
    started = true;
    window._hmt = window._hmt || [];
    window._hmt.push(['_setAutoPageview', false]);
    // The free account uses configured static element IDs for conversions.
    // Do not disable that collector or count clicks as virtual pageviews.
    // Canonical paths merge release/filter/return parameters into one page.
    queue(['_trackPageview', page.pathname]);
    const script = document.createElement('script');
    script.async = true;
    script.src = 'https://hm.baidu.com/hm.js?' + site;
    document.head.appendChild(script);
  }
  function choose(next) {
    if (closing) return;
    choice = next;
    if (!localPreview) { try { localStorage.setItem(key, choice); } catch (_) {} }
    dialog?.close();
    if (next === 'allow') start();
    // A fresh document guarantees no loaded third-party collector remains.
    hideNotice(() => { if (next !== 'allow' && started) location.reload(); });
  }
  if (notice) notice.hidden = choice === 'allow' || choice === 'deny';
  reserveSpace();
  if (notice && typeof ResizeObserver === 'function') new ResizeObserver(reserveSpace).observe(notice);
  addEventListener('resize', reserveSpace);
  document.querySelectorAll('.analytics-privacy').forEach(button => { button.hidden = false; });
  document.addEventListener('click', event => {
    const target = event.target;
    const control = target.closest?.('[data-analytics-choice]');
    if (control) { choose(control.dataset.analyticsChoice); return; }
    if (target.closest?.('[data-analytics-details]')) { dialog?.showModal(); return; }
    if (target.closest?.('[data-analytics-close]')) { dialog?.close(); return; }
    if (choice !== 'allow') return;
    const link = target.closest?.('a[href]');
    if (!link) return;
    const destination = new URL(link.href, location.href);
    let action;
    if (destination.origin === location.origin && destination.hash === '#contact' &&
        /^\/(?:en\/)?about\.html$/.test(destination.pathname)) action = 'entry_click';
    else if (destination.protocol === 'mailto:') action = 'email_click';
    else if (destination.protocol === 'tel:') action = 'phone_click';
    else if (destination.origin === 'https://wa.me') action = 'whatsapp_click';
    else if (destination.origin === location.origin && /\/assets\/wechat-qr\.png$/.test(destination.pathname)) action = 'wechat_qr_click';
    if (!action) return;
    const placements = [
      ['.intro-actions','hero'], ['.service-actions','service_top'],
      ['.case-contact','case_contact'], ['.about-opening','about_top'],
      ['#contact','contact_details'], ['.site-footer','footer'], ['.site-header','header']
    ];
    const placement = placements.find(([selector]) => link.closest(selector))?.[1] || 'content';
    queue(['_trackEvent','consultation',action,page.pathname + '|' + placement]);
  }, {capture:true});
  addEventListener('pageshow', event => {
    if (event.persisted) queue(['_trackPageview', page.pathname]);
  });
  addEventListener('storage', event => {
    if (localPreview || event.key !== key) return;
    if (event.newValue === 'allow') { choice = 'allow'; hideNotice(); start(); }
    else {
      choice = 'deny';
      if (event.newValue === 'deny') hideNotice();
      else { if (notice) notice.hidden = false; reserveSpace(); }
      if (started) location.reload();
    }
  });
  if (choice === 'allow') start();
})();
