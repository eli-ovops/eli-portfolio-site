/* Native solid-surface UI; selected React Bits layout/control adaptations retained.
 * Opaque panels, sliding navigation underline, edge emphasis and step transitions.
 * No glass, glow overlays, pointer-following lighting, navigation interception or new dependencies.
 * Existing carousel, shaders, content and state owners remain independent.
 */
(() => {
  'use strict';
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  const english = document.documentElement.lang === 'en';
  const fine = matchMedia('(hover: hover) and (pointer: fine)');
  document.documentElement.classList.add('bits-ui');
  document.documentElement.dataset.componentSet = 'solid-native';
  document.documentElement.dataset.surfaceStyle = 'solid';
  // Structural panels use an inert edge rule; no lighting layers or pointer loop.
  document.querySelectorAll('.case-facts>div,.about-question').forEach(card=>card.classList.add('bits-panel'));
  // Anchors stay still; only a two-pixel underline moves.
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
      marker.style.transform = `translate(${rect.left-container.left}px,${rect.bottom-container.top-4}px)`;
      marker.style.width = `${rect.width}px`; marker.style.height = '2px';
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
  document.querySelectorAll('.intro-actions .primary,.about-consult,.case-consult-link,.case-contact .text-link').forEach(link=>link.classList.add('bits-action'));
  // Existing reveal controllers animate these inner units; the hit areas stay fixed.
  document.querySelectorAll('.archive-list .archive-meta,.case-type,.capability-role,.about-identity').forEach(label => label.classList.add('bits-eyebrow'));

  // Keep the asymmetric content grid. Interaction is a finite CSS edge reveal;
  // no glare, translucent waves or image perspective tracking.
  document.querySelectorAll('.topic-grid,.capability-grid').forEach(grid=>{
    grid.classList.add('bits-bento-grid');
    [...grid.children].forEach(card=>card.classList.add('bits-bento-tile'));
  });

  // Three visible route stops replace hidden panels and duplicate controls.
  const route=document.querySelector('[data-component="route"]');
  if(route) {
    const stops=[...route.querySelectorAll('.fde-cycle>li')];
    const choose=index=>stops.forEach((stop,i)=>stop.classList.toggle('route-current',i===index));
    stops.forEach((stop,index)=>{
      stop.addEventListener('pointerenter',()=>choose(index));
      stop.addEventListener('focusin',()=>choose(index));
    });
    choose(0);
    const lineObserver=new IntersectionObserver(entries=>entries.forEach(entry=>{
      if(entry.isIntersecting){route.classList.add('route-visible');lineObserver.unobserve(route);}
    }),{threshold:.15});lineObserver.observe(route);
  }
  // Small illustrative motions run once on arrival and once per deliberate interaction.
  const flowTimers=new Map(),flowFrames=new Map();
  const halt=flow=>{
    clearTimeout(flowTimers.get(flow));cancelAnimationFrame(flowFrames.get(flow));
    flowTimers.delete(flow);flowFrames.delete(flow);flow.classList.remove('flow-playing');
  };
  const play=flow=>{
    if(reduced.matches||document.hidden||flow.classList.contains('flow-playing'))return;
    flowFrames.set(flow,requestAnimationFrame(()=>{
      flowFrames.delete(flow);flow.classList.add('flow-playing');
      flowTimers.set(flow,setTimeout(()=>halt(flow),1100));
    }));
  };
  const flows=[...document.querySelectorAll('.mini-flow')];
  const flowObserver=new IntersectionObserver(entries=>entries.forEach(entry=>{
    if(entry.isIntersecting){play(entry.target);flowObserver.unobserve(entry.target);}
  }),{threshold:.5});
  flows.forEach(flow=>{
    flowObserver.observe(flow);
    const item=flow.closest('.topic-card');
    item.addEventListener('pointerenter',()=>{if(fine.matches)play(flow);});
    item.addEventListener('focusin',()=>play(flow));
    item.addEventListener('click',()=>play(flow));
  });
  const stopFlows=()=>flows.forEach(halt);
  reduced.addEventListener('change',()=>{if(reduced.matches)stopFlows();});
  document.addEventListener('visibilitychange',()=>{if(document.hidden)stopFlows();});
  window.addEventListener('pagehide',stopFlows);

  // Animated List keyboard navigation extends the existing selection owner.
  // No nested scroller, fake listbox role, or new return/search state.
  document.querySelectorAll('.archive-list,.case-index').forEach(list=>{
    list.classList.add('bits-animated-list');
    if(list.matches('.archive-list'))list.tabIndex=0;
    list.addEventListener('keydown',event=>{
      if(event.altKey||event.metaKey||event.ctrlKey)return;
      const links=[...list.querySelectorAll('a')].filter(link=>!link.closest('[hidden]'));
      if(!links.length)return;
      let i=links.indexOf(document.activeElement);
      if(event.key==='ArrowDown')i=Math.min(links.length-1,i+1);
      else if(event.key==='ArrowUp')i=i<0?links.length-1:Math.max(0,i-1);
      else if(event.key==='Home')i=0;else if(event.key==='End')i=links.length-1;else return;
      event.preventDefault();links[i].focus();
    });
  });
  const caseIndex=document.querySelector('.case-index');
  if(caseIndex) {
    const indicator=document.createElement('span');indicator.className='bits-reading-indicator';indicator.setAttribute('aria-hidden','true');caseIndex.prepend(indicator);
    const sync=()=>{
      const current=caseIndex.querySelector('a[aria-current]');
      if(!current){indicator.hidden=true;return;}
      indicator.hidden=false;const r=caseIndex.getBoundingClientRect(),box=current.getBoundingClientRect();
      indicator.style.transform=`translateY(${box.top-r.top}px)`;indicator.style.height=`${box.height}px`;
    };
    new MutationObserver(sync).observe(caseIndex,{subtree:true,attributes:true,attributeFilter:['aria-current']});
    new ResizeObserver(sync).observe(caseIndex);sync();
  }

  window.addEventListener('pagehide',() => document.documentElement.classList.remove('bits-page-visible'));
  window.addEventListener('pageshow',() => document.documentElement.classList.add('bits-page-visible'));
})();
