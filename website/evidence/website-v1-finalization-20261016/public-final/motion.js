(() => {
  'use strict';
  const reduce = matchMedia('(prefers-reduced-motion: reduce)');
  const fine = matchMedia('(hover: hover) and (pointer: fine)');
  const root = document.documentElement;
  // Editorial pages already cancel unrelated native transitions on arrival.
  // Cancel on departure instead: a briefly retained snapshot can eat the first
  // click before pagereveal finishes. Keep the shared case-title transition.
  addEventListener('pageswap', event => {
    if (!event.viewTransition || !event.activation?.entry?.url) return;
    const destination = new URL(event.activation.entry.url);
    if (destination.origin !== location.origin) return;
    const from = location.pathname;
    const to = destination.pathname;
    const isLibrary = path => path.endsWith('/records.html');
    const isCase = path => /\/cases\/[^/]+\.html$/.test(path);
    const editorial = isLibrary(to) || isCase(to) || to.endsWith('/about.html');
    const sharedTitle = (isLibrary(from) && isCase(to)) || (isCase(from) && isLibrary(to));
    if (editorial && !sharedTitle) event.viewTransition.skipTransition();
  });
  const gsap = window.gsap;
  if (!gsap) return; // Static content and native controls are the safe fallback.
  const Flip = window.Flip;
  if (Flip) gsap.registerPlugin(Flip);
  const running = new Set();
  const resets = [];
  const detailsInFlight = new Map();
  const revealPending = new Set();
  let filterTween;
  root.classList.add('motion-enhanced');
  root.dataset.motionEngine = 'gsap-' + gsap.version;

  function track(tween) {
    running.add(tween);
    tween.eventCallback('onComplete', () => running.delete(tween));
    tween.eventCallback('onInterrupt', () => running.delete(tween));
    return tween;
  }

  function entrance(element, vars, duration = 0.56, delay = 0) {
    if (reduce.matches) return;
    track(gsap.fromTo(element, vars, {
      opacity: 1, y: 0, rotation: 0, rotationX: 0, yPercent: 0,
      duration, delay, ease: 'power3.out', clearProps: 'opacity,transform', overwrite: 'auto'
    }));
  }

  if (!reduce.matches && !location.hash) {
    document.querySelectorAll('[data-motion-title]').forEach(heading => {
      const lines = [''];
      heading.childNodes.forEach(node => {
        if (node.nodeName === 'BR') lines.push('');
        else lines[lines.length - 1] += node.textContent;
      });
      const fragment = document.createDocumentFragment();
      lines.filter(line => line.trim()).forEach(text => {
        const mask = document.createElement('span');
        const content = document.createElement('span');
        mask.className = 'motion-line';
        content.className = 'motion-line-content';
        content.textContent = text;
        mask.append(content);
        fragment.append(mask);
      });
      heading.replaceChildren(fragment);
    });
    const intro = gsap.timeline({defaults: {ease: 'power3.out', clearProps: 'opacity,transform'}});
    intro.addLabel('signature', 0);
    if (document.querySelector('[data-kinetic-letter]')) {
      intro.from('[data-kinetic-letter]', {opacity: 0, yPercent: 65, rotationX: -40,
        duration: 0.65, stagger: 0.075}, 'signature');
    }
    if (document.querySelector('.motion-line-content')) {
      intro.from('.motion-line-content', {yPercent: 105, duration: 0.7, stagger: 0.08}, 'signature+=0.12');
    }
    if (document.querySelector('.intro-description')) {
      intro.from('.intro-description', {opacity: 0, y: 12, duration: 0.45}, 'signature+=0.28')
        .from('.intro-actions', {opacity: 0, duration: 0.4}, 'signature+=0.38')
        .from('.intro-actions a>span:not(.bits-star-light)', {y: 8, duration: 0.4}, 'signature+=0.38');
    }
    if (document.querySelector('.intro-capabilities')) {
      intro.from('.intro-capabilities li', {opacity:0, y:8, duration:0.35, stagger:0.05}, 'signature+=0.3');
    }
    track(intro);
  }

  function finishDetails(details) {
    const pending = detailsInFlight.get(details);
    if (!pending) return;
    pending.tween.kill();
    gsap.killTweensOf(details.querySelectorAll('p'));
    details.open = pending.open;
    delete details.dataset.motionOpen;
    gsap.set(details, {clearProps: 'height,overflow'});
    gsap.set(details.querySelectorAll('p'), {clearProps: 'opacity,transform'});
    detailsInFlight.delete(details);
    pending.sync();
  }

  window.PortfolioMotion = {
    toggleDetails(details, sync) {
      const open = !(detailsInFlight.get(details)?.open ?? details.open);
      const start = details.getBoundingClientRect().height;
      const previous = detailsInFlight.get(details);
      if (previous) previous.tween.kill();
      gsap.killTweensOf(details.querySelectorAll('p'));
      if (reduce.matches) {
        detailsInFlight.delete(details);
        delete details.dataset.motionOpen;
        gsap.set(details, {clearProps: 'height,overflow'});
        gsap.set(details.querySelectorAll('p'), {clearProps: 'opacity,transform'});
        details.open = open;
        sync();
        return;
      }
      details.style.height = '';
      details.open = true;
      const expanded = details.getBoundingClientRect().height;
      details.open = false;
      const collapsed = details.getBoundingClientRect().height;
      details.open = true;
      details.dataset.motionOpen = String(open);
      gsap.set(details, {height: start, overflow: 'hidden'});
      sync();
      // Height is necessary here: following content must follow native disclosure layout.
      const tween = gsap.to(details, {height: open ? expanded : collapsed,
        duration: 0.3, ease: 'power2.inOut', onComplete: () => finishDetails(details)});
      detailsInFlight.set(details, {open, sync, tween});
      if (open) entrance(details.querySelectorAll('p'), {opacity: 0, y: 6}, 0.24, 0.06);
    },
    filterCards(cards, apply) {
      if (filterTween) { filterTween.progress(1); filterTween.kill(); }
      gsap.killTweensOf(cards);
      gsap.set(cards, {clearProps: 'transform,opacity'});
      if (reduce.matches) { apply(); return; }
      if (!Flip) {
        apply();
        const visible = cards.filter(card => {
          if (card.hidden) return false;
          const rect = card.getBoundingClientRect();
          return rect.bottom > 0 && rect.top < innerHeight;
        });
        if (visible.length) filterTween = gsap.fromTo(visible, {opacity:0, y:10},
          {opacity:1, y:0, duration:0.32, stagger:0.025, ease:'power3.out', clearProps:'opacity,transform'});
        return;
      }
      const state = Flip.getState(cards.filter(card => !card.hidden));
      apply();
      const visible = cards.filter(card => !card.hidden);
      filterTween = Flip.from(state, {targets: visible, duration: 0.42,
        ease: 'power2.inOut', scale: false, prune: true,
        onEnter: elements => gsap.fromTo(elements, {opacity: 0, y: 10},
          {opacity: 1, y: 0, duration: 0.3, clearProps: 'opacity,transform'})});
    }
  };

  // Rolling labels are decorative duplicates; each link retains one accessible name.
  document.querySelectorAll('[data-roll-title]').forEach(link => {
    const text = link.textContent;
    const frame = document.createElement('span');
    const front = document.createElement('span');
    const back = document.createElement('span');
    frame.className = 'roll-title';
    front.className = 'roll-front';
    back.className = 'roll-back';
    front.textContent = back.textContent = text;
    back.setAttribute('aria-hidden', 'true');
    frame.append(front, back);
    link.replaceChildren(frame);
  });

  // Reveal real content in reading order, without changing its final layout.
  if ('IntersectionObserver' in window) {
    const candidates = new Map();
    const add = (selector, kind = 'content', stagger = 0) => {
      document.querySelectorAll(selector).forEach((element, index) => {
        if (element.closest('.depth-enabled')) return;
        candidates.set(element, {kind, delay: (index % 3) * stagger});
      });
    };
    add('[data-reveal]', 'image', 0.08);
    add('.selected-caption', 'content', 0.08);
    add('.topic-symbol', 'symbol', 0.05);
    add('.work-heading, .gallery-tools');
    add('.about-opening h1', 'heading');
    add('.about-opening-intro', 'content');
    add('.records-heading h1', 'heading');
    add('.records-heading p, .archive-tools, .result-count, .archive-list', 'content', 0.055);
    add('.experience-section h2, .experience-section>div');
    add('.fde-method-heading, .fde-lead, .fde-method-content>h3');
    add('.fde-principles>div', 'content', 0.07);
    add('.fde-cycle>li', 'content', 0.065);
    add('.client-section>div:first-child, .project-experience-group>h3');
    add('.project-experience-grid>li', 'content', 0.055);
    add('.contact-section>div, .about-ending');

    const observer = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (!entry.isIntersecting) return;
        const element = entry.target;
        observer.unobserve(element);
        const {kind, delay} = candidates.get(element);
        revealPending.delete(element);
        gsap.set(element, {clearProps: 'opacity,transform,clipPath'});
        if (reduce.matches) return;
        if (kind === 'image') {
          track(gsap.fromTo(element, {opacity: 0, y: 28, clipPath: 'inset(0 0 14% 0)'},
            {opacity: 1, y: 0, clipPath: 'inset(0 0 0% 0)', duration: 0.85,
             delay, ease: 'power3.out', clearProps: 'opacity,transform,clipPath'}));
        } else if (kind === 'symbol') {
          entrance(element, {opacity:0, y:12}, 0.36, delay);
        } else if (kind === 'heading') {
          track(gsap.fromTo(element, {y: 38, opacity: 0, clipPath: 'inset(0 0 90% 0)'},
            {y: 0, opacity: 1, clipPath: 'inset(0 0 0% 0)', duration: 0.95,
             ease: 'power3.out', clearProps: 'opacity,transform,clipPath'}));
        } else {
          entrance(element, {opacity: 0, y: 24}, 0.75, delay);
        }
      });
    }, {threshold: 0.08, rootMargin: '0px 0px -30px 0px'});
    candidates.forEach((_, element) => {
      // Hide only after the library is ready; focus/anchor/reduced mode always stays readable.
      if (!reduce.matches && !element.contains(document.activeElement)) {
        gsap.set(element, {opacity: 0});
        revealPending.add(element);
      }
      observer.observe(element);
    });
    // Keyboard focus must never arrive in visually hidden content.
    document.addEventListener('focusin', event => {
      candidates.forEach((_, element) => {
        if (!element.contains(event.target)) return;
        gsap.killTweensOf(element);
        gsap.set(element, {clearProps: 'opacity,transform,clipPath'});
        revealPending.delete(element);
        observer.unobserve(element);
      });
    });
    // Restored pages retain their settled state rather than replaying hidden sections.
    addEventListener('pagehide', () => {
      observer.disconnect();
      candidates.forEach((_, element) => {
        gsap.set(element, {clearProps: 'opacity,transform,clipPath'});
      });
      revealPending.clear();
    });
  }

  const clamp = (value, min, max) => Math.min(max, Math.max(min, value));
  const pointerAllowed = event => fine.matches && !reduce.matches && event.pointerType !== 'touch';

  document.querySelectorAll('[data-tilt]').forEach(card => {
    const anchor = card.closest('.selected-project');
    let frame = 0;
    let point;
    function reset() {
      cancelAnimationFrame(frame);
      frame = 0;
      card.classList.remove('pointer-active');
      card.style.removeProperty('--tilt-x');
      card.style.removeProperty('--tilt-y');
    }
    card.addEventListener('pointermove', event => {
      if (!pointerAllowed(event)) return;
      point = {x: event.clientX, y: event.clientY};
      if (frame) return;
      frame = requestAnimationFrame(() => {
        frame = 0;
        // Read the untransformed article to prevent a feedback loop from the tilted card.
        const rect = anchor.getBoundingClientRect();
        const width = card.clientWidth;
        const height = card.clientHeight;
        const x = clamp(point.x - rect.left, 0, width);
        const y = clamp(point.y - rect.top, 0, height);
        card.style.setProperty('--tilt-x', `${(0.5 - y / height) * 4}deg`);
        card.style.setProperty('--tilt-y', `${(x / width - 0.5) * 6}deg`);
        card.style.setProperty('--cursor-x', `${clamp(x, 48, width - 48)}px`);
        card.style.setProperty('--cursor-y', `${clamp(y, 48, height - 48)}px`);
        card.classList.add('pointer-active');
      });
    }, {passive: true});
    card.addEventListener('pointerleave', reset);
    card.addEventListener('pointercancel', reset);
    card.addEventListener('blur', reset);
    resets.push(reset);
  });

  document.querySelectorAll('[data-magnetic]').forEach(button => {
    let frame = 0;
    let point;
    function reset() {
      cancelAnimationFrame(frame);
      frame = 0;
      button.style.removeProperty('--magnet-x');
      button.style.removeProperty('--magnet-y');
    }
    button.addEventListener('pointermove', event => {
      if (!pointerAllowed(event)) return;
      point = {x: event.clientX, y: event.clientY};
      if (frame) return;
      frame = requestAnimationFrame(() => {
        frame = 0;
        const rect = button.getBoundingClientRect();
        button.style.setProperty('--magnet-x', `${clamp((point.x - rect.left - rect.width / 2) * 0.14, -8, 8)}px`);
        button.style.setProperty('--magnet-y', `${clamp((point.y - rect.top - rect.height / 2) * 0.2, -6, 6)}px`);
      });
    }, {passive: true});
    button.addEventListener('pointerleave', reset);
    button.addEventListener('pointercancel', reset);
    button.addEventListener('blur', reset);
    resets.push(reset);
  });

  const portrait = document.querySelector('[data-motion-portrait]');
  let scrollFrame = 0;
  function updateScroll() {
    scrollFrame = 0;
    const range = root.scrollHeight - innerHeight;
    root.style.setProperty('--reading-progress', range > 0 ? String(clamp(scrollY / range, 0, 1)) : '0');
    if (portrait) {
      portrait.style.setProperty('--portrait-drift', reduce.matches ? '0px' : `${-Math.min(Math.max(scrollY, 0), 400) * 0.045}px`);
    }
  }
  function scheduleScroll() {
    if (!scrollFrame) scrollFrame = requestAnimationFrame(updateScroll);
  }
  addEventListener('scroll', scheduleScroll, {passive: true});
  addEventListener('resize', scheduleScroll, {passive: true});
  addEventListener('pageshow', scheduleScroll);
  scheduleScroll();

  function resetMotion() {
    resets.forEach(reset => reset());
    if (reduce.matches) {
      revealPending.forEach(element => gsap.set(element, {clearProps: 'opacity,transform,clipPath'}));
      revealPending.clear();
      running.forEach(tween => { tween.progress(1); tween.kill(); });
      if (filterTween) { filterTween.progress(1); filterTween.kill(); }
      const cards = document.querySelectorAll('.gallery-project');
      gsap.killTweensOf(cards);
      gsap.set(cards, {clearProps: 'transform,opacity'});
      detailsInFlight.forEach((_, details) => finishDetails(details));
    }
    scheduleScroll();
  }
  reduce.addEventListener('change', resetMotion);
  fine.addEventListener('change', resetMotion);
  addEventListener('resize', () => {
    detailsInFlight.forEach((_, details) => finishDetails(details));
    if (filterTween) { filterTween.progress(1); filterTween.kill(); }
  });
  addEventListener('pagehide', () => {
    running.forEach(tween => { tween.progress(1); tween.kill(); });
    if (filterTween) { filterTween.progress(1); filterTween.kill(); }
    detailsInFlight.forEach((_, details) => finishDetails(details));
    resets.forEach(reset => reset());
    cancelAnimationFrame(scrollFrame);
    scrollFrame = 0;
  });
})();
