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
  let cards = [], trigger, progressTween, navigationTween, active = -1;
  const position = {value: 0};

  function render(value) {
    const index = Math.max(0, Math.min(cards.length - 1, Math.round(value)));
    stage.dataset.depthPosition = value.toFixed(3);
    cards.forEach((card, i) => {
      const distance = i - value;
      const plane = card.querySelector('.project-image');
      const front = i === index;
      const opacity = distance >= 0 ? Math.max(0, 1 - distance * 0.25) : Math.max(0, 1 + Math.min(0, distance + 0.25) * 2);
      gsap.set(plane, {z: distance >= 0 ? -distance * 380 : -distance * 230,
        x: distance >= 0 ? distance * (innerWidth <= 650 ? 70 : 160) : distance * 32,
        y: distance >= 0 ? -distance * (innerWidth <= 650 ? 60 : 115) : distance * 50,
        opacity: Math.abs(distance) > 3 ? 0 : opacity});
      card.style.zIndex = String(20 - Math.abs(i - index));
      card.classList.toggle('depth-current', front);
      card.inert = !front;
      card.setAttribute('aria-hidden', String(!front));
      if (!front) {
        const caption = card.querySelector('.selected-caption');
        gsap.killTweensOf(caption);
        gsap.set(caption, {clearProps: 'opacity,transform'});
      }
    });
    if (index !== active) {
      active = index;
      const title = cards[index]?.querySelector('h3').textContent || '';
      label.textContent = `${String(index + 1).padStart(2, '0')} / ${String(cards.length).padStart(2, '0')}`;
      stage.setAttribute('aria-label', `代表项目：${title}。向下滚动浏览，或使用方向键及上一项、下一项按钮。`);
      prev.disabled = index <= 0;
      next.disabled = index >= cards.length - 1;
      const caption = cards[index]?.querySelector('.selected-caption');
      if (caption) {
        gsap.killTweensOf(caption);
        gsap.fromTo(caption, {opacity: 0, y: 14}, {opacity: 1, y: 0, duration: 0.32,
          ease: 'power2.out', clearProps: 'opacity,transform'});
      }
    }
  }

  function clear() {
    navigationTween?.kill();
    progressTween?.kill();
    trigger?.kill(true);
    trigger = null;
    section.classList.remove('depth-enabled');
    controls.hidden = true;
    active = -1;
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
    render(0);
    // No wheel/touch interception: ordinary document scrolling drives the scene.
    progressTween = gsap.fromTo(position, {value: 0}, {value: Math.max(0, cards.length - 1), ease: 'none',
      onUpdate: () => render(position.value),
      scrollTrigger: {id: 'eli-depth-gallery', trigger: section, pin: section,
        start: 'top top', end: () => '+=' + Math.max(160, (cards.length - 1) * innerHeight * 0.62),
        scrub: 0.32, invalidateOnRefresh: true, anticipatePin: 1}});
    trigger = progressTween.scrollTrigger;
    stage.dataset.depthCount = String(cards.length);
    ScrollTrigger.refresh();
  }

  function go(index) {
    if (!trigger) return;
    const target = Math.max(0, Math.min(cards.length - 1, index));
    const y = trigger.start + (trigger.end - trigger.start) * target / Math.max(1, cards.length - 1);
    navigationTween?.kill();
    const scroll = {y: scrollY};
    navigationTween = gsap.to(scroll, {y, duration: 0.5, ease: 'power2.inOut',
      onUpdate: () => window.scrollTo(0, scroll.y)});
  }
  prev.addEventListener('click', () => go(active - 1));
  next.addEventListener('click', () => go(active + 1));
  stage.addEventListener('keydown', event => {
    if (event.target !== stage || !trigger) return;
    if (['ArrowDown', 'ArrowRight'].includes(event.key)) { event.preventDefault(); go(active + 1); }
    if (['ArrowUp', 'ArrowLeft'].includes(event.key)) { event.preventDefault(); go(active - 1); }
    if (event.key === 'Home') { event.preventDefault(); go(0); }
    if (event.key === 'End') { event.preventDefault(); go(cards.length - 1); }
  });
  window.addEventListener('wheel', () => navigationTween?.kill(), {passive:true});
  window.addEventListener('touchstart', () => navigationTween?.kill(), {passive:true});
  window.DepthGallery = {filter(apply) {
    const wasReading = trigger && scrollY >= trigger.start && scrollY <= trigger.end;
    clear();
    apply();
    build();
    if (wasReading && trigger) window.scrollTo(0, trigger.start);
  }};
  reduce.addEventListener('change', build);
  window.addEventListener('pagehide', clear);
  window.addEventListener('pageshow', event => { if (event.persisted) build(); });
  document.fonts.ready.then(() => trigger && ScrollTrigger.refresh());
  all.forEach(card => card.querySelector('img')?.addEventListener('load', () => trigger && ScrollTrigger.refresh(), {once:true}));
  build();
})();
