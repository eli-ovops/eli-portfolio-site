/* Circular Carousel: native adaptation of David Haz / React Bits.
 * Ring geometry, eight curved tiles and damped spring from the upstream component.
 * MIT + Commons Clause: assets/vendor/react-bits-pattern-waves/LICENSE.md.
 * Original case DOM is the semantic/reduced-motion fallback and return-state owner.
 */
(() => {
  'use strict';
  const stage = document.querySelector('[data-depth-stage]');
  const gsap = window.gsap;
  if (!stage || !gsap) return;
  const english = document.documentElement.lang === 'en';
  const section = stage.closest('.selected-work');
  const gallery = stage.querySelector('.poster-gallery');
  const all = [...gallery.querySelectorAll('.gallery-project')];
  const controls = stage.querySelector('.depth-controls');
  const label = controls.querySelector('.depth-position');
  const hint = controls.querySelector('[data-depth-hint]');
  const prev = controls.querySelector('[data-depth-prev]');
  const next = controls.querySelector('[data-depth-next]');
  const reduce = matchMedia('(prefers-reduced-motion: reduce)');
  const mobile = matchMedia('(max-width: 650px)');
  const mod = (n, size) => ((n % size) + size) % size;
  const clamp = (n, low, high) => Math.min(high, Math.max(low, n));
  const wrap = n => mod(n + 180, 360) - 180;
  const root = document.createElement('div');
  root.className = 'bits-carousel';
  root.tabIndex = 0;
  root.setAttribute('role', 'region');
  root.setAttribute('aria-roledescription', 'carousel');
  root.setAttribute('aria-label', english ? 'Project images. Drag or use arrow keys.' : '\u6848\u4f8b\u56fe\u7247\uff0c\u53ef\u62d6\u52a8\u6216\u4f7f\u7528\u65b9\u5411\u952e');
  root.innerHTML = '<div class="bits-carousel-stage"><div class="bits-carousel-camera"><div class="bits-carousel-ring"></div></div></div><span class="bits-carousel-floor" aria-hidden="true"></span>';
  stage.insertBefore(root, gallery);
  const camera = root.querySelector('.bits-carousel-camera');
  const ring = root.querySelector('.bits-carousel-ring');
  const ringStage = root.querySelector('.bits-carousel-stage');
  const nav = document.createElement('nav');
  nav.className = 'depth-index';
  nav.setAttribute('aria-label', english ? 'Choose a project' : '\u5feb\u901f\u9009\u62e9\u9879\u76ee');
  const names = english ? ['Sanitaryware inventory','RAG support','Barcode inventory','Law firm office','Charity foundation','AI content workbench','Brand marketing'] : ['\u6d01\u5177\u5e93\u5b58','RAG \u5ba2\u670d','\u626b\u7801\u5e93\u5b58','\u5f8b\u6240 OA','\u6148\u5584\u57fa\u91d1\u4f1a','AI \u5185\u5bb9\u5de5\u4f5c\u53f0','\u5168\u57df\u8425\u9500'];
  const buttons = all.map((card, i) => {
    const button = document.createElement('button');
    button.type = 'button';
    button.textContent = names[i] || card.querySelector('h3').textContent;
    button.addEventListener('click', () => focusCard(cards.indexOf(card)));
    nav.append(button);
    return button;
  });
  all.forEach(card => {
    const source = card.querySelector('.project-image');
    const opener = document.createElement(source.matches('a') ? 'a' : 'button');
    opener.className = 'bits-image-open text-link';
    opener.textContent = english ? 'View image \u2197' : '\u67e5\u770b\u56fe\u7247 \u2197';
    if (source.matches('a')) {
      opener.href = source.href;
      opener.dataset.imageView = '';
      opener.dataset.imageTitle = source.dataset.imageTitle || card.querySelector('h3').textContent;
      opener.dataset.imageNote = source.dataset.imageNote || '';
      opener.dataset.imageAlt = source.dataset.imageAlt || source.querySelector('img')?.alt || opener.dataset.imageTitle;
      opener.setAttribute('aria-haspopup','dialog');
    } else {
      opener.type = 'button';
      opener.textContent = english ? 'Show project process' : '\u67e5\u770b\u9879\u76ee\u8fc7\u7a0b';
      opener.addEventListener('click', () => source.click());
    }
    card.querySelector('.selected-caption').append(opener);
  });
  section.insertBefore(nav, stage);
  let cards = [], faces = [], active = -1, width = 340, height = 230, radius = 400, step = 360 / all.length;
  let angle = 0, velocity = 0, target = 0, raf = 0, last = 0, press = null, suppressClick = false;
  let visible = true, enabled = false, restoreFrame = 0, wheelTimer = 0;
  const isOpen = card => {
    const details = card?.querySelector('.project-process[id]');
    return details?.dataset.motionOpen ? details.dataset.motionOpen === 'true' : !!details?.open;
  };
  let captionMinimum = 0;
  function measureCaptionMinimum() {
    // Measure closed, inert copies so changing the selected project cannot move
    // the next section. Expanded content still grows naturally without clipping.
    captionMinimum = 0;
    cards.forEach(card => {
      const copy = card.cloneNode(true);
      copy.inert = true;
      copy.setAttribute('aria-hidden','true');
      copy.style.cssText = 'position:relative;inset:auto;visibility:hidden;pointer-events:none;';
      copy.removeAttribute('id');
      copy.querySelectorAll('[id]').forEach(node => node.removeAttribute('id'));
      copy.querySelectorAll('details').forEach(details => {
        details.open = false;
        delete details.dataset.motionOpen;
        details.style.removeProperty('height');
      });
      gallery.append(copy);
      captionMinimum = Math.max(captionMinimum, Math.ceil(copy.querySelector('.selected-caption').getBoundingClientRect().height));
      copy.remove();
    });
  }
  function fitCaption() {
    if (!enabled || !cards[active]) return;
    gallery.style.height = `${Math.max(captionMinimum, Math.ceil(cards[active].querySelector('.selected-caption').getBoundingClientRect().height))}px`;
    section.classList.toggle('depth-reading', isOpen(cards[active]));
  }
  function sync(index) {
    if (active === index) return;
    active = index;
    cards.forEach((card, i) => {
      const selected = index === i;
      card.classList.toggle('depth-current', selected);
      card.inert = !selected;
      card.setAttribute('aria-hidden', String(!selected));
      faces[i].setAttribute('aria-pressed', String(selected));
    });
    buttons.forEach((button, i) => button.setAttribute('aria-pressed', String(all[i] === cards[index])));
    label.textContent = `${String(index + 1).padStart(2, '0')} / ${String(cards.length).padStart(2, '0')}`;
    fitCaption();
  }
  function render() {
    if (!enabled) return;
    camera.style.transform = `translateZ(${-radius}px) rotateX(-8deg)`;
    ring.style.transform = `rotateY(${angle}deg)`;
    faces.forEach((face, i) => {
      const facing = Math.cos(wrap(i * step + angle) * Math.PI / 180);
      face.style.transform = `rotateY(${i * step}deg) translateZ(${radius}px)`;
      face.style.setProperty('--cc-depth', (.60 * ((1 - facing) / 2) ** 1.25).toFixed(3));
    });
    stage.dataset.depthPosition = mod(-angle / step, cards.length).toFixed(3);
    sync(mod(Math.round(-angle / step), cards.length));
  }
  function frame(now) {
    raf = 0;
    if (!enabled || document.hidden || !visible) { last = 0; return; }
    let dt = last ? Math.min(.05, (now - last) / 1000) : 1 / 60;
    last = now;
    if (!press?.moved && target !== null) {
      // Upstream critically damped spring; integrate in small stable substeps.
      while (dt > 0) {
        const h = Math.min(dt, 1 / 240);
        velocity += (118 * (target - angle) - 2 * Math.sqrt(118) * velocity) * h;
        angle += velocity * h;
        dt -= h;
      }
      if (Math.abs(target - angle) < .004 && Math.abs(velocity) < .03) {
        angle = target; velocity = 0; target = null;
      }
    }
    render();
    if (target !== null || press?.moved) raf = requestAnimationFrame(frame);
    else last = 0;
  }
  function wake() {
    if (!raf && enabled && visible && !document.hidden) raf = requestAnimationFrame(frame);
  }
  function focusCard(index) {
    if (!enabled || index < 0) return;
    let destination = -index * step;
    destination += 360 * Math.round((angle - destination) / 360);
    target = destination;
    wake();
  }
  function advance(delta) {
    if (!enabled) return;
    const base = target ?? Math.round(angle / step) * step;
    target = base - delta * step;
    wake();
  }
  function measure() {
    if (!enabled) return;
    const room = root.clientWidth;
    width = mobile.matches ? Math.min(310, room * .77) : clamp(room * .32, 240, 380);
    height = width * .66;
    radius = Math.max(cards.length * (width + (mobile.matches ? 18 : 30)) / (2 * Math.PI), width * .6);
    // Desktop fits the whole ring; mobile deliberately peeks at adjacent cards.
    const fit = mobile.matches ? 1 : Math.min(1, room * .96 / (2 * radius + width * .7));
    ringStage.style.transform = `scale(${fit})`;
    root.style.setProperty('--cc-w', `${width}px`);
    root.style.setProperty('--cc-h', `${height}px`);
    root.style.setProperty('--cc-p', `${mobile.matches ? 1600 : 2500}px`);
    faces.forEach(face => {
      face.replaceChildren();
      const source = cards[Number(face.dataset.ccIndex)].querySelector('.project-image');
      const image = source.querySelector('img');
      for (let i = 0; i < 8; i++) {
        const start = i * width / 8 - (i ? 1.25 : 0);
        const end = (i + 1) * width / 8 + (i < 7 ? 1.25 : 0);
        const center = (start + end) / 2 - width / 2;
        const alpha = center / radius;
        const tile = document.createElement('span');
        tile.className = 'bits-carousel-tile';
        tile.setAttribute('aria-hidden','true');
        tile.style.cssText = `left:${-(end-start)/2}px;top:${-height/2}px;width:${end-start}px;height:${height}px;transform:translate3d(${radius*Math.sin(alpha)}px,0,${-radius*(1-Math.cos(alpha))}px) rotateY(${alpha*180/Math.PI}deg)`;
        const picture = document.createElement('span');
        picture.className = 'bits-carousel-picture';
        picture.style.cssText = `left:${-start}px;width:${width}px;height:${height}px;`;
        if (image) {
          const copy = document.createElement('img');
          copy.src = image.currentSrc || image.src;
          copy.alt = ''; copy.draggable = false; copy.decoding = 'async';
          picture.append(copy);
        } else {
          const visual = source.querySelector('.poster-preview,.office-art')?.cloneNode(true);
          if (visual) picture.append(visual);
        }
        tile.append(picture);
        face.append(tile);
      }
    });
    measureCaptionMinimum();
    render(); fitCaption();
  }
  function clear() {
    enabled = false;
    cancelAnimationFrame(raf); raf = 0; last = 0;
    clearTimeout(wheelTimer); press = null;
    root.hidden = true; nav.hidden = true; controls.hidden = true;
    section.classList.remove('depth-enabled','bits-gallery-enabled','depth-reading');
    gallery.style.removeProperty('height');
    all.forEach(card => {
      card.inert = false; card.removeAttribute('aria-hidden'); card.classList.remove('depth-current');
    });
  }
  function build(saved) {
    clear();
    if (reduce.matches) return;
    cards = all.filter(card => !card.hidden);
    if (!cards.length) return;
    enabled = true; active = -1;
    section.classList.add('depth-enabled','bits-gallery-enabled');
    root.hidden = false; nav.hidden = false; controls.hidden = false;
    step = 360 / cards.length;
    const restored = saved ? cards.findIndex(card => card.querySelector('.project-process[id]')?.id === saved.selected) : 0;
    angle = -Math.max(0, restored) * step; target = null; velocity = 0;
    faces = cards.map((card, i) => {
      const face = document.createElement('button');
      face.type = 'button'; face.className = 'bits-carousel-card'; face.tabIndex = -1;
      face.dataset.ccIndex = String(i);
      face.setAttribute('aria-label', (english ? 'Focus project: ' : '\u9009\u62e9\u9879\u76ee\uff1a') + card.querySelector('h3').textContent);
      return face;
    });
    ring.replaceChildren(...faces);
    buttons.forEach((button, i) => { button.hidden = all[i].hidden; });
    prev.disabled = next.disabled = cards.length < 2;
    hint.textContent = mobile.matches ? (english ? 'Swipe sideways or tap arrows' : '\u6a2a\u5411\u62d6\u52a8 \u00b7 \u70b9\u6309\u7bad\u5934\u5207\u6362') : (english ? 'Drag or scroll images to switch' : '\u62d6\u52a8\u6216\u5728\u56fe\u7247\u533a\u6eda\u52a8\u5207\u6362');
    stage.dataset.depthCount = String(cards.length);
    stage.dataset.scrollMode = mobile.matches ? 'page' : 'image-region';
    stage.setAttribute('aria-label', english ? 'Selected projects. Use tabs, drag images or use the arrow buttons.' : '\u4ee3\u8868\u9879\u76ee\uff1a\u53ef\u9009\u62e9\u6807\u7b7e\u3001\u62d6\u52a8\u56fe\u7247\u6216\u4f7f\u7528\u7bad\u5934\u6309\u94ae');
    measure();
  }
  root.addEventListener('pointerdown', event => {
    suppressClick = false;
    if (!enabled || event.button !== 0) return;
    press = {id:event.pointerId,x:event.clientX,y:event.clientY,angle,moved:false,samples:[]};
  });
  root.addEventListener('pointermove', event => {
    if (!press || press.id !== event.pointerId) return;
    const dx = event.clientX - press.x, dy = event.clientY - press.y;
    if (!press.moved) {
      if (Math.abs(dx) < 5) return;
      if (event.pointerType !== 'mouse' && Math.abs(dy) > Math.abs(dx) * 1.2) { press = null; return; }
      press.moved = true; target = null; velocity = 0;
      root.setPointerCapture(event.pointerId); root.dataset.dragging = 'true';
    }
    angle = press.angle + dx * 180 / (Math.PI * radius);
    const now = performance.now();
    press.samples.push({time:now,angle});
    while (press.samples.length > 2 && now - press.samples[0].time > 110) press.samples.shift();
    render();
  });
  function release(event) {
    if (!press || press.id !== event.pointerId) return;
    const current = press; press = null; delete root.dataset.dragging;
    if (!current.moved) return;
    suppressClick = true;
    const first = current.samples[0], end = current.samples.at(-1);
    const span = first && end ? (end.time - first.time) / 1000 : 0;
    velocity = event.type === 'pointercancel' ? 0 : span > .008 ? clamp((end.angle - first.angle) / span,-480,480) : 0;
    target = Math.round((angle + velocity * .18) / step) * step;
    wake();
  }
  root.addEventListener('pointerup', release);
  root.addEventListener('pointercancel', release);
  root.addEventListener('lostpointercapture', release);
  root.addEventListener('dragstart', event => event.preventDefault());
  root.addEventListener('click', event => {
    if (suppressClick) { suppressClick = false; return; }
    const face = event.target.closest('[data-cc-index]');
    if (!face) return;
    focusCard(Number(face.dataset.ccIndex));
  });
  root.addEventListener('wheel', event => {
    if (!enabled || mobile.matches || event.ctrlKey || cards.length < 2) return;
    const delta = Math.abs(event.deltaX) > Math.abs(event.deltaY) ? event.deltaX : event.deltaY;
    if (!delta) return;
    event.preventDefault();
    const scale = event.deltaMode === 1 ? 16 : event.deltaMode === 2 ? root.clientHeight : 1;
    target = null; velocity = 0; angle -= clamp(delta * scale * .13, -step * .45, step * .45);
    render();
    clearTimeout(wheelTimer);
    // A short wheel gesture must finish on the next case, rather than snap
    // back to the same card and appear unresponsive.
    wheelTimer = setTimeout(() => {
      target = (delta > 0 ? Math.floor(angle / step + .001) : Math.ceil(angle / step - .001)) * step;
      wake();
    }, 140);
  }, {passive:false});
  prev.addEventListener('click', () => advance(-1));
  next.addEventListener('click', () => advance(1));
  stage.addEventListener('keydown', event => {
    if (!enabled || ![stage,root].includes(event.target)) return;
    if (event.key === 'ArrowRight') advance(1);
    else if (event.key === 'ArrowLeft') advance(-1);
    else if (event.key === 'Home') focusCard(0);
    else if (event.key === 'End') focusCard(cards.length - 1);
    else return;
    event.preventDefault();
  });
  function save() {
    if (!enabled) return history.state?.portfolioGallery;
    const saved = {selected:cards[active]?.querySelector('.project-process[id]')?.id,
      expanded:all.filter(isOpen).map(card => card.querySelector('.project-process[id]').id), scrollY};
    history.replaceState({...history.state,portfolioGallery:saved},'');
    return saved;
  }
  function restore(saved) {
    if (!saved) { build(); return; }
    all.forEach(card => {
      const details = card.querySelector('.project-process[id]');
      if (!details) return;
      delete details.dataset.motionOpen;
      details.open = saved.expanded?.includes(details.id) || false;
    });
    build(saved);
    history.scrollRestoration = 'manual';
    scrollTo({top:saved.scrollY || 0,behavior:'instant'});
    cancelAnimationFrame(restoreFrame);
    restoreFrame = requestAnimationFrame(() => {
      fitCaption(); scrollTo({top:saved.scrollY || 0,behavior:'instant'});
    });
  }
  all.forEach(card => {
    const details = card.querySelector('.project-process[id]');
    if (!details) return;
    details.addEventListener('toggle',fitCaption);
    new MutationObserver(fitCaption).observe(details,{attributes:true,attributeFilter:['data-motion-open']});
  });
  if ('ResizeObserver' in window) {
    new ResizeObserver(measure).observe(root);
    const captions = new ResizeObserver(fitCaption);
    all.forEach(card => captions.observe(card.querySelector('.selected-caption')));
  }
  new IntersectionObserver(([entry]) => {
    visible = entry.isIntersecting;
    if (visible) wake(); else { cancelAnimationFrame(raf); raf = 0; last = 0; }
  }).observe(root);
  window.DepthGallery = {filter(apply) { const saved = save(); clear(); apply(); build(saved); }};
  reduce.addEventListener('change', () => { const saved = save(); build(saved); });
  mobile.addEventListener('change', () => { const saved = save(); build(saved); });
  document.addEventListener('visibilitychange', () => {
    if (document.hidden) { cancelAnimationFrame(raf); raf = 0; last = 0; } else wake();
  });
  document.addEventListener('pointerdown', () => cancelAnimationFrame(restoreFrame), {capture:true});
  document.addEventListener('wheel', () => cancelAnimationFrame(restoreFrame), {passive:true});
  window.addEventListener('pagehide', () => { save(); cancelAnimationFrame(restoreFrame); clear(); });
  window.addEventListener('pageshow', event => { if (event.persisted) restore(history.state?.portfolioGallery); });
  const returning = performance.getEntriesByType('navigation')[0]?.type === 'back_forward';
  if (returning && history.state?.portfolioGallery) restore(history.state.portfolioGallery);
  else { history.scrollRestoration = 'auto'; build(); }
})();
