/* React Bits FlexCarousel native DOM adaptation. Copyright (c) 2026 David Haz.
 * MIT + Commons Clause: vendor/react-bits-components/LICENSE.md.
 * Official wrap/metrics/nearest/snap and critically damped spring are retained.
 * DOM images replace React/OGL and the liquid-glass lens; autoplay is off.
 * Original semantic case cards own content, image viewing and return context.
 */
(() => {
  'use strict';
  const stage = document.querySelector('[data-depth-stage]');
  if (!stage) return;
  const section = stage.closest('.selected-work');
  const gallery = stage.querySelector('[data-gallery]');
  const all = [...gallery.querySelectorAll('.gallery-project')];
  if (!all.length) return;
  const english = document.documentElement.lang === 'en';
  const reduce = matchMedia('(prefers-reduced-motion: reduce)');
  const controls = stage.querySelector('.depth-controls');
  const label = controls.querySelector('.depth-position');
  const previous = controls.querySelector('[data-depth-prev]');
  const next = controls.querySelector('[data-depth-next]');
  const wrap = (value, size) => ((((value + size / 2) % size) + size) % size) - size / 2;
  const root = document.createElement('div');
  root.className = 'flex-carousel'; root.tabIndex = 0;
  root.setAttribute('role', 'region'); root.setAttribute('aria-roledescription', 'carousel');
  root.setAttribute('aria-label', english ? 'Project images. Drag sideways or use arrow keys.' : '项目图片，可横向拖动或使用方向键');
  stage.insertBefore(root, controls);
  const nav = document.createElement('nav');
  nav.className = 'flex-carousel-index';
  nav.setAttribute('aria-label', english ? 'Choose a project' : '快速选择项目');
  controls.querySelector('[data-depth-hint]').replaceWith(nav);
  const buttons = all.map((card, i) => {
    const button = document.createElement('button'); button.type = 'button';
    button.textContent = card.dataset.galleryLabel || card.querySelector('h3').textContent;
    button.addEventListener('click', () => goTo(cards.indexOf(card)));
    nav.append(button); return button;
  });
  let cards = [], faces = [], layout, active = -1, pos = 0, goal = 0, velocity = 0;
  let raf = 0, last = 0, pointer = null, suppressClick = false, pending = null, visible = true, suspended = false;

  function nearest(at) {
    let best = 0, distance = Infinity;
    layout.centers.forEach((center, i) => {
      const d = Math.abs(wrap(center - at, layout.loop));
      if (d < distance) { best = i; distance = d; }
    });
    return best;
  }
  const snapPoint = at => at + wrap(layout.centers[nearest(at)] - at, layout.loop);
  function sync(index) {
    if (active === index) return;
    active = index;
    cards.forEach((card, i) => {
      const selected = index === i;
      card.classList.toggle('depth-current', selected); card.inert = !selected;
      card.setAttribute('aria-hidden', String(!selected));
      faces[i].setAttribute('aria-pressed', String(selected));
    });
    buttons.forEach((button, i) => button.setAttribute('aria-pressed', String(all[i] === cards[index])));
    label.textContent = `${String(index + 1).padStart(2, '0')} / ${String(cards.length).padStart(2, '0')}`;
  }
  function render() {
    if (!layout) return;
    const center = root.clientWidth / 2;
    const squeeze = reduce.matches ? 1 : 1 - Math.min(Math.abs(velocity) / 3500, 1) * .035;
    faces.forEach((face, i) => {
      const relative = wrap(layout.centers[i] - pos, layout.loop);
      face.style.transform = `translate3d(${center + relative - layout.widths[i] / 2}px,0,0) scale(${squeeze})`;
      face.style.visibility = Math.abs(relative) - layout.widths[i] / 2 > center + 20 ? 'hidden' : 'visible';
    });
    sync(pending ?? nearest(pos));
    stage.dataset.depthPosition = String(active);
  }
  function frame(now) {
    raf = 0;
    if (suspended || !visible || document.hidden) { last = 0; return; }
    let dt = last ? Math.min(.05, Math.max(.001, (now - last) / 1000)) : 1 / 60;
    last = now;
    if (!pointer?.dragging) {
      const stiffness = 55, damping = 2 * Math.sqrt(stiffness);
      const steps = Math.ceil(dt / (1 / 240)), h = dt / steps;
      for (let i = 0; i < steps; i++) {
        velocity += (stiffness * (goal - pos) - damping * velocity) * h;
        pos += velocity * h;
      }
      if (Math.abs(goal - pos) < .05 && Math.abs(velocity) < .5) {
        pos = goal; velocity = 0; pending = null;
      }
    }
    if (Math.abs(pos) > layout.loop * 8) {
      const shift = Math.round(pos / layout.loop) * layout.loop;
      pos -= shift; goal -= shift;
      if (pointer) pointer.startPos -= shift;
    }
    render();
    if (velocity || Math.abs(goal - pos) > .05) raf = requestAnimationFrame(frame);
    else last = 0;
  }
  function wake() {
    if (!raf && visible && !suspended && !document.hidden) raf = requestAnimationFrame(frame);
  }
  function goTo(index) {
    if (index < 0 || !layout) return;
    pending = ((index % cards.length) + cards.length) % cards.length;
    goal += wrap(layout.centers[pending] - goal, layout.loop);
    if (reduce.matches) { pos = goal; velocity = 0; }
    render(); wake();
  }
  function advance(delta) {
    let index = nearest(goal), at = snapPoint(goal);
    const target = (index + delta + cards.length) % cards.length;
    at += Math.sign(delta) * (layout.widths[index] / 2 + layout.gap + layout.widths[target] / 2);
    goal = at; pending = target;
    if (reduce.matches) { pos = goal; velocity = 0; }
    render(); wake();
  }
  function measureCaptions() {
    // Closed panels reserve the same reading area. Open details can still grow.
    let minimum = 0;
    cards.forEach(card => {
      const copy = card.cloneNode(true);
      copy.classList.add('depth-current'); copy.inert = true;
      copy.setAttribute('aria-hidden', 'true');
      copy.removeAttribute('id');
      copy.querySelectorAll('[id]').forEach(node => node.removeAttribute('id'));
      copy.querySelectorAll('details').forEach(details => {
        details.open = false; delete details.dataset.motionOpen;
        details.style.removeProperty('height');
      });
      copy.style.cssText = 'position:absolute;inset:auto;visibility:hidden;pointer-events:none;width:100%;';
      gallery.append(copy);
      minimum = Math.max(minimum, Math.ceil(copy.querySelector('.selected-caption').getBoundingClientRect().height));
      copy.remove();
    });
    gallery.style.minHeight = `${minimum}px`;
  }
  function measure() {
    if (!cards.length) return;
    const width = root.clientWidth, height = root.clientHeight - 20;
    const gap = width < 650 ? 12 : 18;
    const widths = cards.map(card => {
      const img = card.querySelector('img');
      const aspect = img ? (Number(img.getAttribute('width')) || img.naturalWidth) / (Number(img.getAttribute('height')) || img.naturalHeight || 1) : 1.6;
      return Math.min(width * .8, 680, Math.max(.64, Math.min(aspect || 1.6, 2.3)) * height);
    });
    const centers = []; let cursor = 0;
    widths.forEach(w => { centers.push(cursor + w / 2); cursor += w + gap; });
    layout = {widths, centers, gap, loop:Math.max(cursor, 1)};
    faces.forEach((face, i) => { face.style.width = `${widths[i]}px`; });
    pos = goal = centers[Math.max(0, active)]; velocity = 0; pending = null;
    render(); measureCaptions();
  }
  function save() {
    const saved = {selected:cards[active]?.querySelector('.project-process[id]')?.id,
      expanded:all.filter(card => {
        const details = card.querySelector('.project-process[id]');
        return details?.dataset.motionOpen ? details.dataset.motionOpen === 'true' : details?.open;
      }).map(card => card.querySelector('.project-process[id]').id), scrollY};
    history.replaceState({...history.state, portfolioGallery:saved}, ''); return saved;
  }
  function build(saved) {
    cancelAnimationFrame(raf); raf = 0; last = 0; pointer = null; suspended = false;
    cards = all.filter(card => !card.hidden);
    if (!cards.length) return;
    if (saved?.expanded) all.forEach(card => {
      const details = card.querySelector('.project-process[id]');
      if (!details) return;
      delete details.dataset.motionOpen;
      details.open = saved.expanded.includes(details.id);
    });
    faces = cards.map((card, i) => {
      const face = document.createElement('button'); face.type = 'button'; face.className = 'flex-carousel-card';
      face.dataset.flexIndex = String(i); face.tabIndex = -1;
      face.setAttribute('aria-label', (english ? 'Focus project: ' : '选择项目：') + card.querySelector('h3').textContent);
      const image = card.querySelector('.poster-preview,.office-art')?.cloneNode(true);
      if (image) {
        image.setAttribute('aria-hidden', 'true');
        image.querySelectorAll('[id]').forEach(x => x.removeAttribute('id'));
        image.querySelectorAll('img').forEach(img => { img.alt = ''; img.loading = 'eager'; img.draggable = false; });
        face.append(image);
      }
      return face;
    });
    root.replaceChildren(...faces);
    section.classList.add('depth-enabled', 'flex-gallery-enabled'); controls.hidden = false;
    stage.dataset.component = 'flex-carousel-native'; stage.dataset.depthCount = String(cards.length);
    stage.setAttribute('aria-label', english ? 'Selected projects' : '代表项目');
    previous.disabled = next.disabled = cards.length < 2;
    buttons.forEach((button, i) => { button.hidden = all[i].hidden; });
    active = Math.max(0, cards.findIndex(card => card.querySelector('.project-process[id]')?.id === saved?.selected));
    const selected = active; active = -1; sync(selected); measure();
  }
  root.addEventListener('pointerdown', event => {
    if (event.button !== 0) return;
    suppressClick = false; pending = null;
    pointer = {id:event.pointerId, x:event.clientX, y:event.clientY, startPos:pos, dragging:false, samples:[]};
    goal = pos; velocity = 0;
  });
  root.addEventListener('pointermove', event => {
    if (!pointer || pointer.id !== event.pointerId) return;
    const dx = event.clientX - pointer.x, dy = event.clientY - pointer.y;
    if (!pointer.dragging) {
      if (Math.abs(dy) > 10 && Math.abs(dy) > Math.abs(dx)) { pointer = null; goal = snapPoint(pos); wake(); return; }
      if (Math.abs(dx) < (event.pointerType === 'touch' ? 10 : 5)) return;
      pointer.dragging = true; root.setPointerCapture(event.pointerId); root.dataset.dragging = '';
    }
    pos = goal = pointer.startPos - dx;
    const now = performance.now(); pointer.samples.push({x:event.clientX, t:now});
    while (pointer.samples.length > 2 && now - pointer.samples[0].t > 100) pointer.samples.shift();
    render();
  });
  function release(event) {
    if (!pointer || pointer.id !== event.pointerId) return;
    const current = pointer; pointer = null; delete root.dataset.dragging;
    if (!current.dragging) { goal = snapPoint(pos); wake(); return; }
    suppressClick = true;
    const first = current.samples[0], end = current.samples.at(-1);
    velocity = event.type !== 'pointercancel' && first && end && end.t > first.t && performance.now() - end.t < 70
      ? Math.max(-2400, Math.min(2400, -(end.x - first.x) / (end.t - first.t) * 1000)) : 0;
    goal = snapPoint(pos + velocity * .32);
    if (reduce.matches) { pos = goal; velocity = 0; render(); }
    wake();
  }
  root.addEventListener('pointerup', release);
  root.addEventListener('pointercancel', release);
  root.addEventListener('lostpointercapture', release);
  root.addEventListener('dragstart', event => event.preventDefault());
  root.addEventListener('click', event => {
    if (suppressClick) { suppressClick = false; return; }
    const face = event.target.closest('[data-flex-index]'); if (!face) return;
    const index = Number(face.dataset.flexIndex);
    if (index !== active) goTo(index);
    else cards[index].querySelector('[data-image-view]')?.click();
  });
  root.addEventListener('wheel', event => {
    if (event.ctrlKey || Math.abs(event.deltaX) <= Math.abs(event.deltaY)) return;
    event.preventDefault(); pending = null;
    const unit = event.deltaMode === 1 ? 16 : event.deltaMode === 2 ? root.clientWidth : 1;
    advance(event.deltaX * unit > 0 ? 1 : -1);
  }, {passive:false});
  previous.addEventListener('click', () => advance(-1)); next.addEventListener('click', () => advance(1));
  stage.addEventListener('keydown', event => {
    if (![stage, root].includes(event.target)) return;
    if (event.key === 'ArrowRight') advance(1);
    else if (event.key === 'ArrowLeft') advance(-1);
    else if (event.key === 'Home') goTo(0);
    else if (event.key === 'End') goTo(cards.length - 1);
    else if (event.key === 'Enter' || event.key === ' ') cards[active].querySelector('[data-image-view]')?.click();
    else return;
    event.preventDefault();
  });
  window.DepthGallery = {filter(apply) { const saved = save(); apply(); build(saved); }};
  const requested = new URL(location.href).searchParams.get('project');
  const returning = performance.getEntriesByType('navigation')[0]?.type === 'back_forward';
  const saved = returning ? history.state?.portfolioGallery : /^(p\d{2}|n\d{2})$/.test(requested || '') ? {selected:'process-' + requested} : null;
  build(saved);
  new ResizeObserver(measure).observe(root);
  document.fonts.ready.then(measure);
  new IntersectionObserver(([entry]) => { visible = entry.isIntersecting; if (visible) wake(); else { cancelAnimationFrame(raf); raf = 0; last = 0; } }).observe(root);
  reduce.addEventListener('change', () => { if (reduce.matches) { pos = goal; velocity = 0; pending = null; render(); } wake(); });
  document.addEventListener('visibilitychange', () => { if (!document.hidden) wake(); });
  window.addEventListener('pagehide', () => { save(); suspended = true; cancelAnimationFrame(raf); raf = 0; });
  window.addEventListener('pageshow', event => {
    suspended = false;
    if (event.persisted) { const state = history.state?.portfolioGallery; build(state); }
    wake();
  });
})();
