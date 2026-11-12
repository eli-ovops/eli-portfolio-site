/* React Bits adaptations for this static portfolio (David Haz, MIT + Commons Clause).
 * SpotlightCard: pointer-centred fill/edge falloff. PillNav: moving active pill.
 * StarBorder: exact rounded-rectangle outline rendered as an SVG stroke.
 * GlareHover: bounded light band. AnimatedContent uses the existing GSAP owner.
 * No React hydration, external requests, business state or navigation interception.
 */
(() => {
  'use strict';
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  const english = document.documentElement.lang === 'en';
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

  // Magic Bento: one finite wave per grid, plus image-only perspective.
  // The cards and their actual links never tilt or magnetically move.
  const bentoFrames = new Set();
  document.querySelectorAll('.topic-grid,.capability-grid').forEach(grid => {
    grid.classList.add('bits-bento-grid');
    const tiles = [...grid.children];
    let frame = 0;
    tiles.forEach(card => {
      card.classList.add('bits-bento-tile');
      const wave = document.createElement('span'); wave.className='bits-bento-wave';
      wave.setAttribute('aria-hidden','true');card.append(wave);
      card.addEventListener('pointermove',event => {
        if (reduced.matches || !fine.matches) return;
        const r=card.getBoundingClientRect();
        card.style.setProperty('--mb-rx',`${-(event.clientY-r.top-r.height/2)/r.height*5}deg`);
        card.style.setProperty('--mb-ry',`${(event.clientX-r.left-r.width/2)/r.width*6}deg`);
      },{passive:true});
      card.addEventListener('pointerleave',()=>{card.style.setProperty('--mb-rx','0deg');card.style.setProperty('--mb-ry','0deg');});
    });
    const rest=()=>{cancelAnimationFrame(frame);bentoFrames.delete(rest);tiles.forEach(card=>card.style.setProperty('--mb-wa','0'));};
    grid.addEventListener('pointerdown',event => {
      if (reduced.matches || event.button!==0) return;
      rest();const start=performance.now(),rect=grid.getBoundingClientRect();
      const x=event.clientX,y=event.clientY;
      const reach=Math.hypot(Math.max(x-rect.left,rect.right-x),Math.max(y-rect.top,rect.bottom-y));
      const boxes=tiles.map(card=>card.getBoundingClientRect());
      const tick=now=>{
        const p=Math.min(1,(now-start)/950);
        const radius=reach*(1-Math.pow(1-p,2.2)),alpha=Math.pow(1-p,1.3);
        tiles.forEach((card,i)=>{
          card.style.setProperty('--mb-wx',`${x-boxes[i].left}px`);card.style.setProperty('--mb-wy',`${y-boxes[i].top}px`);
          card.style.setProperty('--mb-wr',`${radius}px`);card.style.setProperty('--mb-wa',String(alpha));
        });
        if(p<1&&!reduced.matches&&!document.hidden)frame=requestAnimationFrame(tick);else rest();
      };
      bentoFrames.add(rest);frame=requestAnimationFrame(tick);
    },{passive:true});
  });

  // Stepper: real existing method copy; static HTML keeps all three steps.
  const workflow=document.querySelector('[data-component="stepper"]');
  if (workflow) {
    const panels=[...workflow.querySelectorAll('.fde-cycle>li')];
    const tabs=document.createElement('div');tabs.className='bits-step-tabs';tabs.setAttribute('role','tablist');
    tabs.setAttribute('aria-label',english?'Working together, three steps':'\u5408\u4f5c\u6d41\u7a0b\uff0c\u4e09\u4e2a\u6b65\u9aa4');
    const footer=document.createElement('div');footer.className='bits-step-footer';
    const previous=document.createElement('button'),next=document.createElement('button'),position=document.createElement('span');
    previous.type=next.type='button';previous.textContent=english?'\u2190 Previous':'\u2190 \u4e0a\u4e00\u6b65';next.textContent=english?'Next \u2192':'\u4e0b\u4e00\u6b65 \u2192';
    position.setAttribute('aria-live','polite');footer.append(previous,position,next);
    const list=workflow.querySelector('.fde-cycle');list.before(tabs);list.after(footer);
    const tabButtons=panels.map((panel,index)=>{
      const tab=document.createElement('button');tab.type='button';tab.setAttribute('role','tab');
      tab.id=`workflow-tab-${index+1}`;panel.id=`workflow-panel-${index+1}`;
      tab.setAttribute('aria-controls',panel.id);
      const number=document.createElement('span');number.textContent=String(index+1).padStart(2,'0');number.setAttribute('aria-hidden','true');
      const name=document.createElement('span');name.textContent=panel.querySelector('h4').textContent;tab.append(number,name);
      tab.addEventListener('click',()=>choose(index));
      tab.addEventListener('keydown',event=>{
        let n=index;
        if(event.key==='ArrowRight')n=(index+1)%panels.length;
        else if(event.key==='ArrowLeft')n=(index+panels.length-1)%panels.length;
        else if(event.key==='Home')n=0;else if(event.key==='End')n=panels.length-1;else return;
        event.preventDefault();choose(n);tabButtons[n].focus({preventScroll:true});
      });
      tabs.append(tab);return tab;
    });
    let selected=Math.max(0,Math.min(panels.length-1,history.state?.eliWorkflowStep||0)),animation;
    function choose(index,animate=true) {
      selected=index;animation?.cancel();
      workflow.classList.toggle('bits-stepper-enabled',!reduced.matches);
      tabs.hidden=footer.hidden=reduced.matches;
      panels.forEach((panel,i)=>{
        panel.hidden=!reduced.matches&&i!==selected;
        if(reduced.matches){panel.removeAttribute('role');panel.removeAttribute('aria-labelledby');}
        else {panel.setAttribute('role','tabpanel');panel.setAttribute('aria-labelledby',tabButtons[i].id);}
        tabButtons[i].setAttribute('aria-selected',String(i===selected));tabButtons[i].tabIndex=i===selected?0:-1;
      });
      previous.disabled=selected===0;next.disabled=selected===panels.length-1;
      position.textContent=`${String(selected+1).padStart(2,'0')} / ${String(panels.length).padStart(2,'0')}`;
      workflow.style.setProperty('--step-progress',String(selected/(panels.length-1)));
      if(animate&&!reduced.matches&&panels[selected].animate) {
        const content=panels[selected].querySelector('.workflow-lead');
        animation=content.animate([{opacity:.3,transform:'translateY(10px)'},{opacity:1,transform:'translateY(0)'}],{duration:360,easing:'cubic-bezier(.22,1,.36,1)'});
      }
      try{history.replaceState({...history.state,eliWorkflowStep:selected},'');}catch(_){}
    }
    previous.addEventListener('click',()=>choose(Math.max(0,selected-1)));
    next.addEventListener('click',()=>choose(Math.min(panels.length-1,selected+1)));
    reduced.addEventListener('change',()=>choose(selected,false));
    choose(selected,false);
  }

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

  // Gradient Text: one finite arrival sweep and pointer response, no idle loop.
  const gradientTitles=[...document.querySelectorAll('main h1,.footer-brand')];
  const gradientObserver=new IntersectionObserver(entries=>{
    entries.forEach(entry=>{if(entry.isIntersecting){entry.target.classList.add('bits-gradient-entered');gradientObserver.unobserve(entry.target);}});
  });
  gradientTitles.forEach(title=>{
    title.classList.add('bits-gradient-text');gradientObserver.observe(title);
    title.addEventListener('pointermove',event=>{
      if(reduced.matches||!fine.matches)return;const r=title.getBoundingClientRect();
      title.style.setProperty('--gt-position',`${Math.round((event.clientX-r.left)/r.width*100)}%`);
    },{passive:true});
  });
  window.addEventListener('pagehide',()=>bentoFrames.forEach(stop=>stop()));
  document.addEventListener('visibilitychange',()=>{if(document.hidden)bentoFrames.forEach(stop=>stop());});
  window.addEventListener('pagehide',() => document.documentElement.classList.remove('bits-page-visible'));
  window.addEventListener('pageshow',() => document.documentElement.classList.add('bits-page-visible'));
})();
