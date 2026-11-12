(() => {
  'use strict';
  const section = document.querySelector('.selected-work');
  const stage = document.querySelector('[data-depth-stage]');
  const gsap = window.gsap;
  if (!section || !stage || !gsap) return;
  const reduce = matchMedia('(prefers-reduced-motion: reduce)');
  const all = [...stage.querySelectorAll('.gallery-project')];
  const controls = stage.querySelector('.depth-controls');
  const label = controls.querySelector('.depth-position');
  const prev = controls.querySelector('[data-depth-prev]');
  const next = controls.querySelector('[data-depth-next]');
  const exit = controls.querySelector('[data-depth-exit]');
  const help = document.createElement('p');
  help.className = 'depth-help';
  help.textContent = '区内滚动切换案例 · 区外滚动页面 · Esc 退出';
  controls.insertBefore(help, exit);
  const indexNav = document.createElement('nav');
  indexNav.className = 'depth-index';
  indexNav.setAttribute('aria-label', '快速选择项目');
  const shortNames = ['全域营销', '慈善基金会', '洁具库存', 'RAG 客服', '扫码库存', '织境', '律所 OA'];
  const indexButtons = all.map((card, i) => {
    const button = document.createElement('button');
    button.type = 'button';
    button.textContent = shortNames[i] || card.querySelector('h3').textContent;
    button.setAttribute('aria-label', '查看' + card.querySelector('h3').textContent);
    button.setAttribute('aria-pressed', 'false');
    button.addEventListener('click', () => {
      const destination = cards.indexOf(card);
      if (destination < 0) return;
      let delta = mod(destination - active, cards.length);
      if (delta > cards.length / 2) delta -= cards.length;
      go(Math.round(target) + delta);
    });
    indexNav.append(button);
    return button;
  });
  section.insertBefore(indexNav, stage);

  let cards = [], views = [], smoothing, active = -1, target = 0;
  let snapTimer = 0, touchY = null;
  const position = {value: 0};
  const mod = (value, size) => ((value % size) + size) % size;

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
    });
    if (index === active) return;
    active = index;
    indexButtons.forEach((button, i) => button.setAttribute('aria-pressed', String(all[i] === cards[index])));
    views.forEach((view, i) => {
      const front = i === index;
      view.card.style.zIndex = String(20 - mod(i - index, cards.length));
      view.card.classList.toggle('depth-current', front);
      view.card.inert = !front;
      view.card.setAttribute('aria-hidden', String(!front));
      gsap.killTweensOf(view.caption);
      gsap.set(view.caption, {clearProps: 'opacity,transform'});
    });
    label.textContent = `${String(index + 1).padStart(2, '0')} / ${String(cards.length).padStart(2, '0')}`;
    stage.setAttribute('aria-label', `代表项目：${views[index].title}。鼠标位于展示区时滚动切换，区外正常滚动页面；也可用方向键或前后按钮。`);
    prev.disabled = next.disabled = cards.length <= 1;
    gsap.fromTo(views[index].caption, {opacity: 0, y: 9}, {opacity: 1, y: 0,
      duration: 0.5, ease: 'sine.out', clearProps: 'opacity,transform'});
  }

  function clear() {
    clearTimeout(snapTimer);
    smoothing?.tween.kill();
    smoothing = null;
    section.classList.remove('depth-enabled');
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

  function build() {
    clear();
    if (reduce.matches) return;
    cards = all.filter(card => !card.hidden);
    if (!cards.length) return;
    section.classList.add('depth-enabled');
    controls.hidden = false;
    indexNav.hidden = false;
    indexButtons.forEach((button, i) => { button.hidden = all[i].hidden; });
    position.value = 0;
    views = cards.map(card => ({card, caption:card.querySelector('.selected-caption'),
      title:card.querySelector('h3').textContent,
      set:gsap.quickSetter(card.querySelector('.project-image'), 'css')}));
    render(0);
    smoothing = gsap.quickTo(position, 'value', {duration:0.5, ease:'power2.out',
      onUpdate:() => render(position.value)});
    stage.dataset.depthCount = String(cards.length);
    stage.dataset.scrollMode = 'pointer-region';
  }

  function go(value) {
    if (!smoothing || cards.length <= 1) return;
    clearTimeout(snapTimer);
    target = value;
    smoothing(target);
  }

  function captionCanScroll(element, delta) {
    const caption = element instanceof Element ? element.closest('.selected-caption') : null;
    if (!caption || caption.scrollHeight <= caption.clientHeight + 1) return false;
    return delta > 0 ? caption.scrollTop + caption.clientHeight < caption.scrollHeight - 1 : caption.scrollTop > 1;
  }

  function canCapture() {
    const rect = stage.getBoundingClientRect();
    return rect.top >= -8 && rect.bottom <= innerHeight + 8;
  }

  function leaveScene() {
    clearTimeout(snapTimer);
    document.querySelector('footer')?.scrollIntoView({behavior:reduce.matches ? 'auto' : 'smooth', block:'start'});
  }

  function gesture(delta) {
    target += Math.max(-1.4, Math.min(1.4, delta / Math.max(360, stage.clientHeight * 0.65)));
    smoothing(target);
    clearTimeout(snapTimer);
    snapTimer = setTimeout(() => {
      // Finish a gesture on a fully readable case, including the circular seam.
      go(delta > 0 ? Math.ceil(target - 0.001) : Math.floor(target + 0.001));
    }, 180);
  }

  stage.addEventListener('wheel', event => {
    if (!smoothing || cards.length <= 1 || event.ctrlKey || !canCapture()) return;
    let delta = Math.abs(event.deltaY) >= Math.abs(event.deltaX) ? event.deltaY : event.deltaX;
    if (event.deltaMode === 1) delta *= 16;
    if (event.deltaMode === 2) delta *= stage.clientHeight;
    if (!delta || captionCanScroll(event.target, delta)) return;
    // This handler exists only on the scene: outside it, the browser owns scrolling.
    event.preventDefault();
    gesture(delta);
  }, {passive:false});

  stage.addEventListener('touchstart', event => {
    touchY = event.touches.length === 1 ? event.touches[0].clientY : null;
  }, {passive:true});
  stage.addEventListener('touchmove', event => {
    if (!smoothing || cards.length <= 1 || touchY === null || event.touches.length !== 1 || !canCapture()) return;
    const y = event.touches[0].clientY;
    const delta = touchY - y;
    if (Math.abs(delta) < 6) return;
    touchY = y;
    if (captionCanScroll(event.target, delta)) return;
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
  exit.addEventListener('click', leaveScene);

  window.DepthGallery = {filter(apply) { clear(); apply(); build(); }};
  reduce.addEventListener('change', build);
  window.addEventListener('resize', () => { if (smoothing) render(position.value); });
  window.addEventListener('pagehide', clear);
  window.addEventListener('pageshow', event => { if (event.persisted) build(); });
  build();
})();
