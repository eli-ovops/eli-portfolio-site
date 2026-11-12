(() => {
  'use strict';
  document.querySelectorAll('[data-article-rotator]').forEach(root => {
    const viewport = root.querySelector('[data-article-window]');
    const track = viewport?.querySelector('.article-list');
    const template = root.querySelector('[data-article-pool]');
    const pool = [...(template?.content.querySelectorAll('.article-row') || [])];
    const controls = root.querySelector('.article-preview-controls');
    const pause = root.querySelector('[data-article-pause]');
    const next = root.querySelector('[data-article-next]');
    if (!track || pool.length < 3 || !controls || !pause || !next) return;

    const english = document.documentElement.lang === 'en';
    const reduced = matchMedia('(prefers-reduced-motion: reduce)');
    const pointer = matchMedia('(hover: hover)');
    let index = 0, rowSize = 0, timer = 0, animation = null;
    let userPaused = false, hovered = false, focused = false, visible = false;
    let width = 0, resizeFrame = 0;
    const clearTimer = () => { clearTimeout(timer); timer = 0; };
    const blocked = () => !visible || document.hidden || hovered || focused;
    const clone = number => pool[number % pool.length].cloneNode(true);

    function sync() {
      clearTimer();
      root.dataset.rotation = userPaused || reduced.matches ? 'paused' : blocked() ? 'waiting' : 'playing';
      pause.hidden = reduced.matches;
      pause.setAttribute('aria-pressed', String(userPaused));
      const label = userPaused ? (english ? 'Resume rotation' : '继续轮播') : (english ? 'Pause rotation' : '暂停轮播');
      pause.setAttribute('aria-label', label);
      pause.title = label;
      pause.firstElementChild.textContent = userPaused ? '▶' : 'Ⅱ';
      if (animation) {
        if (blocked() || userPaused) animation.pause();
        else animation.play();
      } else if (!blocked() && !userPaused && !reduced.matches && rowSize) {
        timer = setTimeout(advance, 7000);
      }
    }

    function settle() {
      track.firstElementChild.remove();
      index = (index + 1) % pool.length;
      const finished = animation;
      animation = null;
      // Remove the translated first row before releasing the final transform.
      // The remaining two rows therefore stay at exactly their current positions.
      finished?.cancel();
      root.dataset.position = String(index);
      track.lastElementChild.removeAttribute('aria-hidden');
      track.lastElementChild.inert = false;
      sync();
    }

    function advance() {
      clearTimer();
      if (animation || !rowSize || document.hidden || focused) return;
      const incoming = clone(index + 2);
      incoming.setAttribute('aria-hidden', 'true');
      incoming.inert = true;
      track.append(incoming);
      if (reduced.matches || !track.animate) { settle(); return; }
      animation = track.animate([
        { transform: 'translateY(0)' },
        { transform: `translateY(-${rowSize}px)` }
      ], { duration: 680, easing: 'cubic-bezier(.32,0,.2,1)', fill: 'forwards' });
      animation.onfinish = settle;
    }

    function measure() {
      const currentWidth = viewport.getBoundingClientRect().width;
      if (!currentWidth) return;
      width = currentWidth;
      if (animation) {
        animation.onfinish = null;
        animation.cancel();
        animation = null;
        track.lastElementChild.remove();
      }
      const measuring = document.createElement('div');
      measuring.className = 'article-preview-measure';
      measuring.inert = true;
      measuring.setAttribute('aria-hidden', 'true');
      pool.forEach(row => measuring.append(row.cloneNode(true)));
      viewport.append(measuring);
      rowSize = Math.ceil(Math.max(...[...measuring.children].map(row => row.getBoundingClientRect().height)));
      measuring.remove();
      root.style.setProperty('--article-row-size', `${rowSize}px`);
      root.dataset.ready = 'true';
      controls.hidden = false;
      sync();
    }

    pause.addEventListener('click', () => { userPaused = !userPaused; sync(); });
    next.addEventListener('click', () => {
      // Manual stepping remains available while automatic rotation is paused.
      if (animation) {
        animation.onfinish = null;
        settle();
      } else advance();
    });
    viewport.addEventListener('pointerenter', () => { hovered = pointer.matches; sync(); });
    viewport.addEventListener('pointerleave', () => { hovered = false; sync(); });
    viewport.addEventListener('focusin', () => { focused = true; sync(); });
    viewport.addEventListener('focusout', () => {
      queueMicrotask(() => { focused = viewport.contains(document.activeElement); sync(); });
    });
    document.addEventListener('visibilitychange', sync);
    reduced.addEventListener('change', () => {
      if (animation && reduced.matches) { animation.onfinish = null; settle(); }
      sync();
    });
    new IntersectionObserver(entries => {
      visible = entries[0].isIntersecting;
      sync();
    }, { threshold: .2 }).observe(viewport);
    new ResizeObserver(() => {
      if (Math.abs(viewport.getBoundingClientRect().width - width) < 1) return;
      cancelAnimationFrame(resizeFrame);
      resizeFrame = requestAnimationFrame(measure);
    }).observe(viewport);
    root.dataset.position = '0';
    measure();
    document.fonts?.ready.then(measure);
  });
})();
