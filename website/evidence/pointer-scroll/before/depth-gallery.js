(() => {
  'use strict';
  const section = document.querySelector('.selected-work');
  const stage = document.querySelector('[data-depth-stage]');
  const gsap = window.gsap;
  const ScrollTrigger = window.ScrollTrigger;
  if (!section || !stage || !gsap || !ScrollTrigger) return;
  gsap.registerPlugin(ScrollTrigger);
  const reduce = matchMedia('(prefers-reduced-motion: reduce)');
  const all = [...stage.querySelectorAll('.gallery-project')];
  const controls = stage.querySelector('.depth-controls');
  const label = controls.querySelector('.depth-position');
  const prev = controls.querySelector('[data-depth-prev]');
  const next = controls.querySelector('[data-depth-next]');
  const exit = controls.querySelector('[data-depth-exit]');
  let cards = [], views = [], trigger, smoothing, navigationTween, active = -1;
  let cycleOffset = 0, wrapping = false, looping = true, navigationTarget = null;
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
    stage.setAttribute('aria-label', `代表项目：${views[index].title}。首尾循环，使用滚动、方向键或前后按钮浏览。`);
    prev.disabled = next.disabled = cards.length <= 1;
    gsap.fromTo(views[index].caption, {opacity: 0, y: 9}, {opacity: 1, y: 0,
      duration: 0.5, ease: 'sine.out', clearProps: 'opacity,transform'});
  }

  function clear() {
    navigationTween?.kill();
    smoothing?.tween.kill();
    trigger?.kill(true);
    trigger = null;
    section.classList.remove('depth-enabled');
    controls.hidden = true;
    active = -1;
    navigationTarget = null;
    all.forEach(card => {
      card.inert = false;
      card.removeAttribute('aria-hidden');
      card.classList.remove('depth-current');
      card.style.removeProperty('z-index');
      gsap.killTweensOf(card.querySelector('.selected-caption'));
      gsap.set(card.querySelectorAll('.project-image,.selected-caption'), {clearProps: 'opacity,transform'});
    });
  }

  function build() {
    clear();
    if (reduce.matches) { ScrollTrigger.refresh(); return; }
    cards = all.filter(card => !card.hidden);
    if (!cards.length) return;
    section.classList.add('depth-enabled');
    controls.hidden = false;
    position.value = 0;
    cycleOffset = 0;
    looping = true;
    views = cards.map(card => {
      const plane = card.querySelector('.project-image');
      return {card, caption:card.querySelector('.selected-caption'),
        title:card.querySelector('h3').textContent, set:gsap.quickSetter(plane, 'css')};
    });
    render(0);
    smoothing = gsap.quickTo(position, 'value', {duration:0.55, ease:'power2.out', onUpdate:() => render(position.value)});
    // Native page scrolling supplies the target; only the loop boundary is recentered.
    trigger = ScrollTrigger.create({id:'eli-depth-gallery', trigger:section, pin:section,
      start:'top top', end:() => '+=' + Math.max(300, cards.length > 1 ? cards.length * innerHeight * 0.62 * 3 : 160),
      anticipatePin:1,
      onUpdate(self) {
        if (wrapping) return;
        let raw = self.progress * cards.length * 3;
        const span = (self.end - self.start) / (cards.length * 3);
        if (looping && self.isActive && !navigationTween?.isActive() && cards.length > 1 && raw > cards.length * 2 + 0.35) {
          wrapping = true;
          cycleOffset += cards.length;
          raw -= cards.length;
          window.scrollTo({top:self.start + raw * span, behavior:'instant'});
          ScrollTrigger.update();
          wrapping = false;
        } else if (looping && !navigationTween?.isActive() && cycleOffset !== 0 && raw < 0.05 && self.isActive) {
          wrapping = true;
          cycleOffset -= cards.length;
          raw += cards.length;
          window.scrollTo({top:self.start + raw * span, behavior:'instant'});
          ScrollTrigger.update();
          wrapping = false;
        }
        smoothing(raw + cycleOffset);
      }
    });
    stage.dataset.depthCount = String(cards.length);
    ScrollTrigger.refresh();
  }

  function go(target) {
    if (!trigger) return;
    looping = true;
    navigationTween?.kill();
    navigationTarget = target;
    const span = (trigger.end - trigger.start) / (cards.length * 3);
    const oldOffset = cycleOffset;
    let raw = target - cycleOffset;
    while (raw < 0.05) { raw += cards.length; cycleOffset -= cards.length; }
    while (raw > cards.length * 3 - 0.1) { raw -= cards.length; cycleOffset += cards.length; }
    if (oldOffset !== cycleOffset) {
      wrapping = true;
      window.scrollTo({top:scrollY + (oldOffset - cycleOffset) * span, behavior:'instant'});
      ScrollTrigger.update();
      wrapping = false;
    }
    const scroll = {y:scrollY};
    navigationTween = gsap.to(scroll, {y:trigger.start + raw * span, duration:0.55,
      ease:'power2.inOut', onUpdate:() => window.scrollTo({top:scroll.y, behavior:'instant'}),
      onComplete:() => { if (navigationTarget === target) navigationTarget = null; }});
  }
  prev.addEventListener('click', () => go(Math.round(navigationTarget ?? position.value) - 1));
  next.addEventListener('click', () => go(Math.round(navigationTarget ?? position.value) + 1));
  stage.addEventListener('keydown', event => {
    if (event.target !== stage || !trigger) return;
    if (['ArrowDown', 'ArrowRight'].includes(event.key)) { event.preventDefault(); go(Math.round(navigationTarget ?? position.value) + 1); }
    if (['ArrowUp', 'ArrowLeft'].includes(event.key)) { event.preventDefault(); go(Math.round(navigationTarget ?? position.value) - 1); }
    if (event.key === 'Home') { event.preventDefault(); go(0); }
    if (event.key === 'End') { event.preventDefault(); go(cards.length - 1); }
  });
  exit.addEventListener('click', () => {
    if (!trigger) return;
    looping = false;
    navigationTween?.kill();
    window.scrollTo({top:trigger.end + 4, behavior:'instant'});
  });
  window.addEventListener('wheel', () => { navigationTween?.kill(); navigationTarget = null; }, {passive:true});
  window.addEventListener('touchstart', () => { navigationTween?.kill(); navigationTarget = null; }, {passive:true});
  window.DepthGallery = {filter(apply) {
    const wasReading = trigger && scrollY >= trigger.start && scrollY <= trigger.end;
    clear();
    apply();
    build();
    if (wasReading && trigger) window.scrollTo({top:trigger.start, behavior:'instant'});
  }};
  reduce.addEventListener('change', build);
  window.addEventListener('resize', () => {
    if (!trigger) return;
    navigationTween?.kill();
    navigationTarget = null;
    ScrollTrigger.refresh();
    render(position.value);
  });
  window.addEventListener('pagehide', clear);
  window.addEventListener('pageshow', event => { if (event.persisted) build(); });
  document.fonts.ready.then(() => trigger && ScrollTrigger.refresh());
  all.forEach(card => card.querySelector('img')?.addEventListener('load', () => trigger && ScrollTrigger.refresh(), {once:true}));
  build();
})();
