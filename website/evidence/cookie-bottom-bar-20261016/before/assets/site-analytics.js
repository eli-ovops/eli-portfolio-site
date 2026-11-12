(() => {
  'use strict';
  const ownScript = document.currentScript;
  const site = ownScript?.dataset.baiduSite;
  const canonical = document.querySelector('link[rel="canonical"]')?.href;
  if (location.origin !== 'https://www.eliai.cn' || !/^[a-f0-9]{32}$/.test(site || '') || !canonical) return;
  const page = new URL(canonical);
  if (page.origin !== location.origin || document.documentElement.dataset.eliAnalytics) return;
  document.documentElement.dataset.eliAnalytics = 'ready';
  const key = 'eli-analytics-consent-' + ownScript.dataset.consentVersion;
  const notice = document.getElementById('analytics-notice');
  const dialog = document.getElementById('analytics-dialog');
  let choice;
  try { choice = localStorage.getItem(key); } catch (_) {}
  let started = false;
  const queue = value => { if (started && choice === 'allow') window._hmt.push(value); };
  function start() {
    if (started) return;
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
    choice = next;
    try { localStorage.setItem(key, choice); } catch (_) {}
    if (notice) notice.hidden = true;
    dialog?.close();
    if (next === 'allow') start();
    // A fresh document guarantees no loaded third-party collector remains.
    else if (started) location.reload();
  }
  if (notice) notice.hidden = choice === 'allow' || choice === 'deny';
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
    if (event.key !== key) return;
    if (event.newValue === 'allow') { choice = 'allow'; if (notice) notice.hidden = true; start(); }
    else { choice = 'deny'; if (notice) notice.hidden = event.newValue === 'deny'; if (started) location.reload(); }
  });
  if (choice === 'allow') start();
})();
