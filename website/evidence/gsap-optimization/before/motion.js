(() => {
  'use strict';
  const reduce = matchMedia('(prefers-reduced-motion: reduce)');
  const fine = matchMedia('(hover: hover) and (pointer: fine)');
  const root = document.documentElement;
  const easing = 'cubic-bezier(0.16, 1, 0.3, 1)';
  const running = new Set();
  const resets = [];
  const canAnimate = typeof Element.prototype.animate === 'function';
  root.classList.add('motion-enhanced');

  function play(element, frames, duration, delay = 0) {
    if (reduce.matches || !canAnimate) return;
    const animation = element.animate(frames, {duration, delay, easing, fill: 'backwards'});
    running.add(animation);
    // Remove completed effects so hover transforms and responsive layout stay native.
    animation.finished.then(() => {
      running.delete(animation);
      animation.cancel();
    }, () => running.delete(animation));
  }

  // Only split explicit lines. Chinese text continues wrapping at the viewport width.
  document.querySelectorAll('[data-kinetic-letter]').forEach((letter, index) => {
    if (location.hash) return;
    play(letter, [{opacity: 0, transform: 'translateY(65%) rotateX(-50deg)'},
                  {opacity: 1, transform: 'translateY(0) rotateX(0)'}], 580, index * 75);
  });

  document.querySelectorAll('[data-motion-title]').forEach(heading => {
    if (reduce.matches || !canAnimate || location.hash) return;
    const lines = [''];
    heading.childNodes.forEach(node => {
      if (node.nodeName === 'BR') lines.push('');
      else lines[lines.length - 1] += node.textContent;
    });
    const fragment = document.createDocumentFragment();
    lines.filter(line => line.trim()).forEach((text, index) => {
      const mask = document.createElement('span');
      const content = document.createElement('span');
      mask.className = 'motion-line';
      content.className = 'motion-line-content';
      content.textContent = text;
      mask.append(content);
      fragment.append(mask);
      play(content, [
        {transform: 'translateY(105%) rotate(1.5deg)'},
        {transform: 'translateY(0) rotate(0)'}
      ], 740, index * 90);
    });
    heading.replaceChildren(fragment);
  });

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

  if ('IntersectionObserver' in window) {
    const observer = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (!entry.isIntersecting) return;
        const element = entry.target;
        observer.unobserve(element);
        if (element.dataset.reveal === 'image') {
          play(element, [
            {clipPath: 'inset(0 0 100% 0 round 14px)', transform: 'translateY(34px)'},
            {clipPath: 'inset(0 0 0 0 round 14px)', transform: 'translateY(0)'}
          ], 560, Number(element.dataset.motionDelay || 0));
        } else {
          play(element, [{opacity: 0, transform: 'translateY(22px)'},
                         {opacity: 1, transform: 'translateY(0)'}], 560);
        }
      });
    }, {threshold: 0.12, rootMargin: '0px 0px -20px 0px'});
    document.querySelectorAll('[data-reveal]').forEach((element, index) => {
      element.dataset.motionDelay = String(element.dataset.reveal === 'image' ? (index % 3) * 45 : 0);
      observer.observe(element);
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
    if (reduce.matches) running.forEach(animation => animation.cancel());
    scheduleScroll();
  }
  reduce.addEventListener('change', resetMotion);
  fine.addEventListener('change', resetMotion);
  addEventListener('pagehide', () => {
    running.forEach(animation => animation.cancel());
    resets.forEach(reset => reset());
    cancelAnimationFrame(scrollFrame);
    scrollFrame = 0;
  });
})();
