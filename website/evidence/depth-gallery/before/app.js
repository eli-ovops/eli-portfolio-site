(() => {
  'use strict';
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
      cover.setAttribute('aria-label', `${open ? '收起' : '展开'} ${title} 案例`);
      details.querySelector('summary').textContent = open ? '收起项目过程 −' : '查看项目过程 ＋';
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

  const gallery = document.querySelector('[data-gallery]');
  if (gallery) {
    const cards = [...gallery.querySelectorAll('[data-gallery-type]')];
    const buttons = [...document.querySelectorAll('[data-gallery-filter]')];
    const count = document.querySelector('.gallery-count');
    document.querySelector('[data-gallery-tools]').hidden = false;
    buttons.forEach(button => button.addEventListener('click', () => {
      const category = button.dataset.galleryFilter;
      buttons.forEach(item => item.setAttribute('aria-pressed', String(item === button)));
      const apply = () => {
        let visible = 0;
        cards.forEach(card => {
          card.hidden = category !== 'all' && card.dataset.galleryType !== category;
          if (!card.hidden) visible++;
        });
        count.textContent = `${visible} 个案例`;
      };
      if (window.PortfolioMotion) window.PortfolioMotion.filterCards(cards, apply);
      else apply();
    }));
  }

  const input = document.querySelector('#search');
  if (!input) return;
  const disclosure = document.querySelector('.archive-disclosure');
  const items = [...disclosure.querySelectorAll('.archive-list li')];
  const filters = [...document.querySelectorAll('[data-filter]')];
  const countLabel = document.querySelector('.result-count');
  const empty = document.querySelector('.empty');
  const reset = document.querySelector('.reset-search');
  let category = '全部';
  document.querySelector('[data-enhance]').hidden = false;

  function restore() {
    const params = new URLSearchParams(location.search);
    const requested = params.get('category');
    category = filters.some(button => button.dataset.filter === requested) ? requested : '全部';
    input.value = params.get('q') || '';
    if (category !== '全部' || input.value) disclosure.open = true;
    update(false);
  }

  function update(save = true) {
    const query = input.value.trim().toLocaleLowerCase();
    let count = 0;
    filters.forEach(button => button.setAttribute('aria-pressed', String(button.dataset.filter === category)));
    items.forEach(item => {
      const match = (category === '全部' || item.dataset.category === category)
        && item.dataset.search.toLocaleLowerCase().includes(query);
      item.hidden = !match;
      if (match) count++;
    });
    countLabel.textContent = `${count} 项记录`;
    empty.hidden = count !== 0;
    if (save) {
      const url = new URL(location.href);
      category === '全部' ? url.searchParams.delete('category') : url.searchParams.set('category', category);
      input.value ? url.searchParams.set('q', input.value) : url.searchParams.delete('q');
      history.replaceState(null, '', url);
    }
  }

  filters.forEach(button => button.addEventListener('click', () => {
    category = button.dataset.filter;
    update();
  }));
  input.addEventListener('input', () => update());
  reset.addEventListener('click', () => {
    category = '全部';
    input.value = '';
    update();
    input.focus();
  });
  window.addEventListener('popstate', restore);
  window.addEventListener('pageshow', restore);
  restore();
})();
