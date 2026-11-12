/* React Bits adaptations for this static portfolio (David Haz, MIT + Commons Clause).
 * SpotlightCard: pointer-centred fill/edge falloff. PillNav: moving active pill.
 * StarBorder: exact rounded-rectangle outline rendered as an SVG stroke.
 * GlareHover: bounded light band. AnimatedContent uses the existing GSAP owner.
 * No React hydration, external requests, business state or navigation interception.
 */
(() => {
  'use strict';
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  const fine = matchMedia('(hover: hover) and (pointer: fine)');
  document.documentElement.classList.add('bits-ui');
  document.documentElement.dataset.componentSet = 'react-bits-native';
  const ns = 'http://www.w3.org/2000/svg';
  const cards = [...document.querySelectorAll('.capability-card,.customer-topic,.customer-topic-card,.topic-card,.fde-map,.fde-cycle>li,.case-facts>div,.about-question,.archive-list>li,.case-related a,.related-projects a')];
  cards.forEach(card => {
    card.classList.add('bits-spotlight');
    const glow = document.createElement('span');
    glow.className = 'bits-spotlight-fill'; glow.setAttribute('aria-hidden','true');
    const edge = document.createElement('span');
    edge.className = 'bits-spotlight-edge'; edge.setAttribute('aria-hidden','true');
    card.append(glow, edge);
    const move = event => {
      if (!fine.matches || reduced.matches) return;
      const box = card.getBoundingClientRect();
      card.style.setProperty('--spot-x', `${event.clientX - box.left}px`);
      card.style.setProperty('--spot-y', `${event.clientY - box.top}px`);
    };
    card.addEventListener('pointermove',move,{passive:true});
    card.addEventListener('pointerleave',() => {
      card.style.removeProperty('--spot-x'); card.style.removeProperty('--spot-y');
    });
  });
  // Keep the navigation's real anchors still. Only this inert pill moves.
  const nav = document.querySelector('.site-header>nav');
  if (nav) {
    const marker = document.createElement('span');
    marker.className = 'bits-nav-marker'; marker.setAttribute('aria-hidden','true');
    nav.prepend(marker);
    const current = nav.querySelector('[aria-current="page"]');
    const sync = link => {
      if (!link) { marker.hidden = true; return; }
      marker.hidden = false;
      const container = nav.getBoundingClientRect(), rect = link.getBoundingClientRect();
      marker.style.transform = `translate(${rect.left-container.left}px,${rect.top-container.top}px)`;
      marker.style.width = `${rect.width}px`; marker.style.height = `${rect.height}px`;
    };
    const links = [...nav.querySelectorAll('a')];
    links.forEach(link => {
      link.addEventListener('pointerenter',() => { if (fine.matches) sync(link); });
      link.addEventListener('focus',() => sync(link));
    });
    nav.addEventListener('pointerleave',() => sync(current));
    nav.addEventListener('focusout',event => { if (!nav.contains(event.relatedTarget)) sync(current); });
    new ResizeObserver(() => sync(current)).observe(nav);
    document.fonts.ready.then(() => sync(current));
    window.addEventListener('pageshow',() => sync(current));
    sync(current);
  }
  const stars = [...document.querySelectorAll('.intro-actions .primary,.about-consult,.case-consult-link,.case-contact .text-link')];
  stars.forEach(link => {
    link.classList.add('bits-star');
    const svg = document.createElementNS(ns,'svg');
    svg.classList.add('bits-star-light'); svg.setAttribute('aria-hidden','true');
    const rect = document.createElementNS(ns,'rect');
    rect.setAttribute('fill','none'); rect.setAttribute('pathLength','100'); rect.setAttribute('rx','22');
    svg.append(rect); link.append(svg);
    new ResizeObserver(() => {
      const box = link.getBoundingClientRect();
      svg.setAttribute('viewBox',`0 0 ${box.width} ${box.height}`);
      rect.setAttribute('x','1'); rect.setAttribute('y','1');
      rect.setAttribute('width',String(Math.max(0,box.width-2)));
      rect.setAttribute('height',String(Math.max(0,box.height-2)));
    }).observe(link);
  });
  document.querySelectorAll('.capability-image,.detail-image a,.detail-image[data-image-view]').forEach(image => {
    image.classList.add('bits-glare');
    const band = document.createElement('span');
    band.className = 'bits-glare-band'; band.setAttribute('aria-hidden','true'); image.append(band);
  });
  // Existing reveal controllers animate these inner units; the hit areas stay fixed.
  document.querySelectorAll('.archive-list .archive-meta,.case-type,.capability-role,.about-identity').forEach(label => label.classList.add('bits-eyebrow'));
  window.addEventListener('pagehide',() => document.documentElement.classList.remove('bits-page-visible'));
  window.addEventListener('pageshow',() => document.documentElement.classList.add('bits-page-visible'));
})();
