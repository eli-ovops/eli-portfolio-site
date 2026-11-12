(() => {
  'use strict';
  const english = document.documentElement.lang === 'en';
  const allCategory = english ? 'All' : '全部';
  const clientCategory = english ? 'Client work' : '客户参与';
  const languageSwitch = document.querySelector('.language-switch');
  if (languageSwitch) languageSwitch.addEventListener('click', () => {
    languageSwitch.hash = location.hash;
  });
  const nav = [...document.querySelectorAll('[data-nav]')];
  const defaultNav = nav.find(link => link.hasAttribute('aria-current'));
  const sections = nav.map(link => document.getElementById(link.dataset.nav)).filter(Boolean);
  // Native links remain usable without JS. Highlight only the section currently read.
  if (sections.length && 'IntersectionObserver' in window) {
    const visible = new Set();
    const observer = new IntersectionObserver(entries => {
      entries.forEach(entry => entry.isIntersecting ? visible.add(entry.target.id) : visible.delete(entry.target.id));
      const current = sections.find(section => visible.has(section.id));
      nav.forEach(link => {
        if (current?.id === link.dataset.nav) link.setAttribute('aria-current', 'location');
        else if (!current && link === defaultNav) link.setAttribute('aria-current', 'page');
        else link.removeAttribute('aria-current');
      });
    }, {rootMargin: '-20% 0px -65% 0px'});
    sections.forEach(section => observer.observe(section));
  }

  document.querySelectorAll('.gallery-project').forEach(card => {
    const details = card.querySelector('.project-process[id]');
    const toggles = [...card.querySelectorAll('[data-case-toggle]')];
    if (!details) return;
    const sync = () => {
      const open = details.dataset.motionOpen ? details.dataset.motionOpen === 'true' : details.open;
      toggles.forEach(button => button.setAttribute('aria-expanded', String(open)));
      const cover = card.querySelector('.project-image');
      const title = card.querySelector('h3').textContent.replace(/[＋−]/g, '').trim();
      if (cover.hasAttribute('data-image-view')) cover.setAttribute('aria-label', english ? `View ${title} screenshot` : `查看 ${title} 截图`);
      else cover.setAttribute('aria-label', english ? `${open ? 'Collapse' : 'Expand'} ${title} project` : `${open ? '收起' : '展开'} ${title} 案例`);
      details.querySelector('summary').textContent = english ? (open ? 'Hide project process −' : 'Project process ＋') : (open ? '收起项目过程 −' : '查看项目过程 ＋');
    };
    const toggle = () => {
      if (window.PortfolioMotion) window.PortfolioMotion.toggleDetails(details, sync);
      else { details.open = !details.open; sync(); }
    };
    toggles.forEach(button => button.addEventListener('click', toggle));
    details.querySelector('summary').addEventListener('click', event => {
      if (!window.PortfolioMotion) return;
      event.preventDefault();
      toggle();
    });
    details.addEventListener('toggle', sync);
    sync();
  });

  const input = document.querySelector('#search');
  if (!input) return;
  const disclosure = document.querySelector('.archive-disclosure');
  const items = [...disclosure.querySelectorAll('.archive-list li')];
  const filters = [...document.querySelectorAll('[data-filter]')];
  const countLabel = document.querySelector('.result-count');
  const empty = document.querySelector('.empty');
  const reset = document.querySelector('.reset-search');
  let category = allCategory;
  document.querySelector('[data-enhance]').hidden = false;

  function restore() {
    const params = new URLSearchParams(location.search);
    const requested = params.get('category');
    category = filters.some(button => button.dataset.filter === requested) ? requested : allCategory;
    input.value = params.get('q') || '';
    if (category !== allCategory || input.value) disclosure.open = true;
    update(false);
  }

  function update(save = true) {
    const query = input.value.trim().toLocaleLowerCase();
    let count = 0;
    filters.forEach(button => button.setAttribute('aria-pressed', String(button.dataset.filter === category)));
    items.forEach(item => {
      const match = (category === allCategory || item.dataset.category === category
        || (category === clientCategory && item.dataset.client === 'true'))
        && item.dataset.search.toLocaleLowerCase().includes(query);
      item.hidden = !match;
      if (match) count++;
    });
    countLabel.textContent = english ? `${count} ${count === 1 ? "project" : "projects"}` : `${count} 项记录`;
    empty.hidden = count !== 0;
    if (save) {
      const url = new URL(location.href);
      category === allCategory ? url.searchParams.delete('category') : url.searchParams.set('category', category);
      input.value ? url.searchParams.set('q', input.value) : url.searchParams.delete('q');
      history.replaceState(null, '', url);
    }
  }

  filters.forEach(button => button.addEventListener('click', () => {
    category = button.dataset.filter;
    if (window.PortfolioMotion) window.PortfolioMotion.filterCards(items, () => update());
    else update();
  }));
  input.addEventListener('input', () => update());
  // Keep an active search editor focused through a mouse reset. Letting the
  // press blur it, then refocusing inside click, can recommit its old text.
  reset.addEventListener('mousedown', event => {
    if (event.button === 0 && document.activeElement === input) event.preventDefault();
  });
  reset.addEventListener('click', () => {
    category = allCategory;
    input.value = '';
    update();
    input.focus();
  });
  window.addEventListener('popstate', restore);
  window.addEventListener('pageshow', restore);
  restore();
})();
