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
  document.querySelectorAll('.capability-card,.topic-card,.case-facts>div,.about-question').forEach(card=>card.classList.add('bits-panel'));
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

  window.addEventListener('pagehide',() => document.documentElement.classList.remove('bits-page-visible'));
  window.addEventListener('pageshow',() => document.documentElement.classList.add('bits-page-visible'));
})();
