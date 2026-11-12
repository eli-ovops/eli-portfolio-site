/* Progressive enhancement. All article links remain in static HTML. */
(() => {
  const root = document.querySelector('[data-article-library]');
  if (!root) {
    const back = document.querySelector('[data-article-back]');
    const languageLink = document.querySelector('.language-switch');
    if (back) {
      try {
        const expected = new URL(back.href, location.href);
        const saved = sessionStorage.getItem('eli-article-list-' + document.documentElement.lang);
        const previous = saved && new URL(saved, location.origin);
        if (previous && previous.origin === expected.origin && previous.pathname === expected.pathname) {
          for (const key of ['q','category','page']) {
            const value = previous.searchParams.get(key);
            if (value) expected.searchParams.set(key,value);
          }
          back.href = expected.href;
        }
      } catch (_) {}
    }
    if (languageLink) {
      const syncAnchor = () => {
        const target = new URL(languageLink.href, location.href);
        target.hash = location.hash && document.getElementById(location.hash.slice(1)) ? location.hash : '';
        languageLink.href = target.href;
      };
      syncAnchor();
      addEventListener('hashchange', syncAnchor);
      languageLink.addEventListener('click', () => {
        // Carry the current list context across a detail-page language switch.
        // Only copy query fields into the exact paired article-list path.
        try {
          const source = new URL(back.href, location.href);
          const target = new URL(languageLink.href, location.href);
          if (source.origin !== location.origin || target.origin !== location.origin) return;
          const targetLang = document.documentElement.lang === 'en' ? 'zh-CN' : 'en';
          const list = new URL('../articles.html', target);
          for (const key of ['q','category','page']) {
            const value = source.searchParams.get(key);
            if (value) list.searchParams.set(key,value);
          }
          sessionStorage.setItem('eli-article-list-' + targetLang,list.pathname + list.search);
        } catch (_) {}
      });
    }
    return;
  }
  const form = root.querySelector('form');
  const rows = [...root.querySelectorAll('.article-row')];
  const controls = root.querySelector('[data-library-pages]');
  const status = root.querySelector('[data-library-status]');
  const empty = root.querySelector('[data-library-empty]');
  const en = document.documentElement.lang === 'en';
  const size = 12;
  let page = 1;
  const normalized = value => value.normalize('NFKC').toLocaleLowerCase().trim();
  const text = rows.map(row => normalized(row.dataset.search || row.textContent));
  function fromURL() {
    const params = new URL(location.href).searchParams;
    form.elements.q.value = params.get('q') || '';
    form.elements.category.value = params.get('category') || 'all';
    if (!form.elements.category.value) form.elements.category.value = 'all';
    page = Math.max(1, Number.parseInt(params.get('page'), 10) || 1);
  }
  function update(save = true) {
    const query = normalized(form.elements.q.value);
    const category = form.elements.category.value;
    const words = query.split(/\s+/).filter(Boolean);
    const matches = rows.filter((row, i) => (category === 'all' || row.dataset.category === category) && words.every(word => text[i].includes(word)));
    const count = matches.length;
    const pages = Math.max(1, Math.ceil(count / size));
    page = Math.min(page, pages);
    rows.forEach(row => { row.hidden = true; });
    matches.slice((page - 1) * size, page * size).forEach(row => { row.hidden = false; });
    empty.hidden = count > 0;
    controls.hidden = count <= size;
    root.querySelector('[data-library-prev]').disabled = page === 1;
    root.querySelector('[data-library-next]').disabled = page === pages;
    root.querySelector('[data-library-page]').textContent = `${page} / ${pages}`;
    status.textContent = en ? `${count} ${count === 1 ? "article" : "articles"} · page ${page} of ${pages}` : `${count} 篇文章 · 第 ${page} / ${pages} 页`;
    if (save) {
      const url = new URL(location.href);
      for (const key of ['q','category','page']) url.searchParams.delete(key);
      if (query) url.searchParams.set('q', form.elements.q.value.trim());
      if (category !== 'all') url.searchParams.set('category',category);
      if (page > 1) url.searchParams.set('page',String(page));
      history.replaceState(null,'',url);
    }
    try { sessionStorage.setItem('eli-article-list-' + document.documentElement.lang, location.pathname + location.search); } catch (_) {}
    const switcher = document.querySelector('.language-switch');
    if (switcher) {
      const url = new URL(switcher.href, location.href);
      for (const key of ['q','category','page']) {
        url.searchParams.delete(key);
        const value = new URL(location.href).searchParams.get(key);
        if (value) url.searchParams.set(key,value);
      }
      switcher.href = url.href;
    }
  }
  form.hidden = false;
  fromURL(); update(false);
  form.addEventListener('submit',event => { event.preventDefault(); page=1; update(); });
  form.addEventListener('input',() => { page=1; update(); });
  form.addEventListener('change',() => { page=1; update(); });
  form.addEventListener('reset',event => { event.preventDefault(); form.elements.q.value=''; form.elements.category.value='all'; page=1; update(); form.elements.q.focus(); });
  function turnPage(offset) { page += offset; update(); status.scrollIntoView({block:'start',behavior:'auto'}); }
  root.querySelector('[data-library-prev]').addEventListener('click',() => turnPage(-1));
  root.querySelector('[data-library-next]').addEventListener('click',() => turnPage(1));
  addEventListener('popstate',() => { fromURL(); update(false); });
})();
