(() => {
  'use strict';
  const english = document.documentElement.lang === 'en';
  const section = document.querySelector('.selected-work');
  const stage = document.querySelector('[data-depth-stage]');
  const gsap = window.gsap;
  if (!section || !stage || !gsap) return;
  const reduce = matchMedia('(prefers-reduced-motion: reduce)');
  const mobile = matchMedia('(max-width: 650px)');
  const gallery = stage.querySelector('.poster-gallery');
  const all = [...stage.querySelectorAll('.gallery-project')];
  const controls = stage.querySelector('.depth-controls');
  const label = controls.querySelector('.depth-position');
  const prev = controls.querySelector('[data-depth-prev]');
  const next = controls.querySelector('[data-depth-next]');
  const hint = controls.querySelector('[data-depth-hint]');
  const indexNav = document.createElement('nav');
  indexNav.className = 'depth-index';
  indexNav.setAttribute('aria-label', english ? 'Choose a project' : '快速选择项目');
  const indexButtons = all.map((card, i) => {
    const button = document.createElement('button');
    button.type = 'button';
    button.textContent = card.dataset.galleryLabel || card.querySelector('h3').textContent;
    button.setAttribute('aria-label', (english ? 'View ' : '查看') + card.querySelector('h3').textContent);
    button.setAttribute('aria-pressed', 'false');
    button.addEventListener('click', () => {
      const destination = cards.indexOf(card);
      if (destination < 0) return;
      let delta = mod(destination - mod(Math.round(target), cards.length), cards.length);
      if (delta > cards.length / 2) delta -= cards.length;
      go(Math.round(target) + delta);
    });
    indexNav.append(button);
    return button;
  });
  section.insertBefore(indexNav, stage);

  let cards = [], views = [], smoothing, active = -1, target = 0;
  let snapTimer = 0, touchY = null, galleryBaseHeight = 0, restoreFrame = 0;
  const position = {value: 0};
  const mod = (value, size) => ((value % size) + size) % size;

  function storyOpen(card) {
    const story = card?.querySelector('.project-process[id]');
    return story?.dataset.motionOpen ? story.dataset.motionOpen === 'true' : !!story?.open;
  }

  function updateReadingMode() {
    const reading = storyOpen(cards[active]);
    section.classList.toggle('depth-reading', reading);
    stage.dataset.scrollMode = mobile.matches ? 'page' : 'pointer-region';
    hint.textContent = mobile.matches
      ? (english ? 'Use tabs or arrows to switch · scroll to read' : '标签或箭头切换 · 滚动阅读')
      : (english ? 'Scroll on the image to switch · scroll text to read' : '图片上滚动切换 · 正文滚动阅读');
    const title = views[active]?.title || '';
    stage.setAttribute('aria-label', english
      ? `Selected project: ${title}. ${hint.textContent}.`
      : `代表项目：${title}。${hint.textContent}。`);
  }

  function fitMobileStory() {
    if (!section.classList.contains('depth-enabled')) {
      gallery.style.removeProperty('height');
      return;
    }
    const card = cards[active];
    if (!card) return;
    if (mobile.matches) gallery.style.height = `${Math.ceil(card.getBoundingClientRect().height)}px`;
    else if (storyOpen(card)) gallery.style.height = `${Math.max(galleryBaseHeight, Math.ceil(card.querySelector('.selected-caption').scrollHeight))}px`;
    else gallery.style.removeProperty('height');
  }

  function render(value) {
    if (!cards.length) return;
    const index = mod(Math.round(value), cards.length);
    stage.dataset.depthPosition = mod(value, cards.length).toFixed(3);
    views.forEach((view, i) => {
      let distance = mod(i - value, cards.length);
      if (distance > cards.length - 1) distance -= cards.length;
      if (cards.length === 1) distance = 0;
      const opacity = distance >= 0 ? Math.max(0, 1 - distance * 0.3) : Math.max(0, 1 + Math.min(0, distance + 0.4) * 2);
      view.set({z: distance >= 0 ? -distance * 380 : -distance * 180,
        x: distance >= 0 ? distance * (innerWidth <= 650 ? 44 : 90) : distance * 18,
        y: distance >= 0 ? -distance * (innerWidth <= 650 ? 58 : 140) : distance * 30,
        opacity: Math.abs(distance) > 3 ? 0 : opacity});
      // Text follows the same continuous position as the image, fading to zero
      // at the midpoint so two descriptions never overlap.
      let captionDistance = mod(i - value + cards.length / 2, cards.length) - cards.length / 2;
      if (cards.length === 1) captionDistance = 0;
      view.setCaption({opacity: Math.max(0, 1 - Math.abs(captionDistance) * 2),
        y: Math.max(-18, Math.min(18, captionDistance * 18))});
    });
    if (index === active) return;
    active = index;
    updateReadingMode();
    fitMobileStory();
    indexButtons.forEach((button, i) => button.setAttribute('aria-pressed', String(all[i] === cards[index])));
    views.forEach((view, i) => {
      const front = i === index;
      view.card.style.zIndex = String(20 - mod(i - index, cards.length));
      view.card.classList.toggle('depth-current', front);
      view.card.inert = !front;
      view.card.setAttribute('aria-hidden', String(!front));
    });
    label.textContent = `${String(index + 1).padStart(2, '0')} / ${String(cards.length).padStart(2, '0')}`;
    prev.disabled = next.disabled = cards.length <= 1;
  }

  function clear() {
    clearTimeout(snapTimer);
    smoothing?.tween.kill();
    smoothing = null;
    section.classList.remove('depth-enabled', 'depth-reading', 'stack-gallery-enabled');
    gallery.style.removeProperty('height');
    controls.hidden = true;
    indexNav.hidden = true;
    active = -1;
    target = 0;
    touchY = null;
    all.forEach(card => {
      card.inert = false;
      card.removeAttribute('aria-hidden');
      card.classList.remove('depth-current');
      card.style.removeProperty('z-index');
      gsap.killTweensOf(card.querySelector('.selected-caption'));
      gsap.set(card.querySelectorAll('.project-image,.selected-caption'), {clearProps:'opacity,transform'});
    });
  }

  function build(saved) {
    clear();
    if (reduce.matches) return;
    cards = all.filter(card => !card.hidden);
    if (!cards.length) return;
    section.classList.add('depth-enabled', 'stack-gallery-enabled');
    stage.dataset.component = 'original-stacked-gallery';
    controls.hidden = false;
    indexNav.hidden = false;
    indexButtons.forEach((button, i) => { button.hidden = all[i].hidden; });
    const restoredIndex = saved ? cards.findIndex(card => card.querySelector('.project-process[id]')?.id === saved.selected) : -1;
    target = position.value = Math.max(0, restoredIndex);
    galleryBaseHeight = gallery.getBoundingClientRect().height;
    views = cards.map(card => ({card, caption:card.querySelector('.selected-caption'),
      title:card.querySelector('h3').textContent,
      setCaption:gsap.quickSetter(card.querySelector('.selected-caption'), 'css'),
      set:gsap.quickSetter(card.querySelector('.project-image'), 'css')}));
    render(position.value);
    smoothing = gsap.quickTo(position, 'value', {duration:0.5, ease:'power2.out',
      onUpdate:() => render(position.value)});
    stage.dataset.depthCount = String(cards.length);
  }

  function go(value) {
    if (!smoothing || cards.length <= 1) return;
    clearTimeout(snapTimer);
    target = value;
    smoothing(target);
  }

  function isImageGesture(element) {
    const card = cards[active];
    return !!card && !storyOpen(card) && element instanceof Element
      && element.closest('.project-image') === card.querySelector('.project-image');
  }

  function leaveScene() {
    clearTimeout(snapTimer);
    document.querySelector('footer')?.scrollIntoView({behavior:reduce.matches ? 'auto' : 'smooth', block:'start'});
  }

  function gesture(delta) {
    const step = Math.max(-0.35, Math.min(0.35, delta / Math.max(360, stage.clientHeight * 0.65)));
    target = Math.max(position.value - 1.1, Math.min(position.value + 1.1, target + step));
    smoothing(target);
    clearTimeout(snapTimer);
    snapTimer = setTimeout(() => {
      // Finish a gesture on a fully readable case, including the circular seam.
      go(delta > 0 ? Math.ceil(target - 0.001) : Math.floor(target + 0.001));
    }, 180);
  }

  stage.addEventListener('wheel', event => {
    if (mobile.matches || !smoothing || cards.length <= 1 || event.ctrlKey || !isImageGesture(event.target)) return;
    let delta = Math.abs(event.deltaY) >= Math.abs(event.deltaX) ? event.deltaY : event.deltaX;
    if (event.deltaMode === 1) delta *= 16;
    if (event.deltaMode === 2) delta *= stage.clientHeight;
    if (!delta) return;
    // Only a collapsed current image owns switching. Text and controls scroll naturally.
    event.preventDefault();
    gesture(delta);
  }, {passive:false});

  stage.addEventListener('touchstart', event => {
    touchY = event.touches.length === 1 ? event.touches[0].clientY : null;
  }, {passive:true});
  stage.addEventListener('touchmove', event => {
    if (mobile.matches || !smoothing || cards.length <= 1 || touchY === null || event.touches.length !== 1) return;
    const y = event.touches[0].clientY;
    const delta = touchY - y;
    if (Math.abs(delta) < 6) return;
    touchY = y;
    if (!isImageGesture(event.target)) return;
    event.preventDefault();
    gesture(delta * 2);
  }, {passive:false});
  stage.addEventListener('touchend', () => { touchY = null; }, {passive:true});
  stage.addEventListener('touchcancel', () => { touchY = null; }, {passive:true});

  prev.addEventListener('click', () => go(Math.round(target) - 1));
  next.addEventListener('click', () => go(Math.round(target) + 1));
  stage.addEventListener('keydown', event => {
    if (event.key === 'Escape' && smoothing) { event.preventDefault(); leaveScene(); return; }
    if (event.target !== stage || !smoothing) return;
    if (['ArrowDown','ArrowRight'].includes(event.key)) { event.preventDefault(); go(Math.round(target) + 1); }
    if (['ArrowUp','ArrowLeft'].includes(event.key)) { event.preventDefault(); go(Math.round(target) - 1); }
    if (event.key === 'Home') { event.preventDefault(); go(0); }
    if (event.key === 'End') { event.preventDefault(); go(cards.length - 1); }
  });

  function saveReadingState() {
    const selected = cards[active] || all[0];
    const saved = {selected: selected?.querySelector('.project-process[id]')?.id,
      expanded: all.filter(storyOpen).map(card => card.querySelector('.project-process[id]').id),
      scrollY: window.scrollY};
    // Entry-local state restores Back/Forward without carrying old choices into new visits.
    history.replaceState({...history.state, portfolioGallery: saved}, '');
    return saved;
  }

  function restoreReadingState(saved) {
    if (!saved) return;
    history.scrollRestoration = 'manual';
    all.forEach(card => {
      const details = card.querySelector('.project-process[id]');
      delete details.dataset.motionOpen;
      details.open = saved.expanded?.includes(details.id) || false;
    });
    build(saved);
    window.scrollTo({top: Math.max(0, saved.scrollY || 0), behavior:'instant'});
    cancelAnimationFrame(restoreFrame);
    // Restore after layout and browser-native history scrolling, without a smooth jump.
    restoreFrame = requestAnimationFrame(() => {
      restoreFrame = requestAnimationFrame(() => {
        fitMobileStory();
        window.scrollTo({top: Math.max(0, saved.scrollY || 0), behavior:'instant'});
      });
    });
  }

  all.forEach(card => {
    const details = card.querySelector('.project-process[id]');
    let wasOpen = storyOpen(card);
    const syncReading = () => {
      const opening = !wasOpen && storyOpen(card);
      wasOpen = storyOpen(card);
      if (card !== cards[active]) return;
      if (opening && details.dataset.motionOpen === 'true' && smoothing) {
        clearTimeout(snapTimer);
        smoothing.tween.pause();
        target = position.value = active;
        render(active);
      }
      updateReadingMode();
      fitMobileStory();
    };
    details.addEventListener('toggle', syncReading);
    new MutationObserver(syncReading).observe(details, {attributes:true, attributeFilter:['data-motion-open']});
  });

  window.DepthGallery = {filter(apply) { clear(); apply(); build(); }};
  reduce.addEventListener('change', () => { const saved = saveReadingState(); build(saved); });
  mobile.addEventListener('change', () => {
    active = -1;
    if (smoothing) render(position.value);
    updateReadingMode();
  });
  if ('ResizeObserver' in window) {
    const storyObserver = new ResizeObserver(fitMobileStory);
    all.forEach(card => { storyObserver.observe(card); storyObserver.observe(card.querySelector('.selected-caption')); });
  }
  window.addEventListener('resize', () => {
    gallery.style.removeProperty('height');
    galleryBaseHeight = gallery.getBoundingClientRect().height;
    if (smoothing) render(position.value);
    fitMobileStory();
  });
  window.addEventListener('pagehide', () => { history.scrollRestoration = 'manual'; saveReadingState(); cancelAnimationFrame(restoreFrame); clear(); });
  // A new user action takes precedence over a pending restoration frame.
  document.addEventListener('pointerdown', () => cancelAnimationFrame(restoreFrame), {capture:true});
  document.addEventListener('wheel', () => cancelAnimationFrame(restoreFrame), {passive:true});
  window.addEventListener('pageshow', event => { if (event.persisted) restoreReadingState(history.state?.portfolioGallery); });
  const returning = performance.getEntriesByType('navigation')[0]?.type === 'back_forward';
  if (returning && history.state?.portfolioGallery) restoreReadingState(history.state.portfolioGallery);
  else {
    history.scrollRestoration = 'auto';
    all.forEach(card => { card.querySelector('.project-process[id]').open = false; });
    history.replaceState({...history.state, portfolioGallery:null}, '');
    const project = new URL(location.href).searchParams.get('project');
    build(/^(p\d{2}|n\d{2})$/.test(project || '') ? {selected:'process-'+project} : undefined);
  }
})();
