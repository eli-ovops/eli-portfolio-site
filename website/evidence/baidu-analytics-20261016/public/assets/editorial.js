(() => {
  'use strict';
  const main = document.querySelector('main');
  const gsap = window.gsap;
  document.documentElement.dataset.editorialStatus = !main ? 'no-main' : !gsap ? 'missing-gsap' : 'ready';
  if (!main || !gsap) return;
  const reduce = matchMedia('(prefers-reduced-motion: reduce)');
  const Flip = window.Flip;
  const ScrollTrigger = window.ScrollTrigger;
  if (Flip) gsap.registerPlugin(Flip);
  if (ScrollTrigger) gsap.registerPlugin(ScrollTrigger);
  document.documentElement.classList.add('motion-enhanced');
  document.documentElement.dataset.motionEngine = 'gsap-' + gsap.version;
  const timing = {change:.42, reveal:main.classList.contains('records-main') ? .64 : .46,
    title:main.classList.contains('about-main') ? .8 : .76};
  const running = new Set();
  const finished = new WeakSet();
  const rows = [...document.querySelectorAll('.archive-list li')];
  let revealObserver, filterTween, filtering = false, scrollFrame = 0;
  let syncCategory;
  let workflowTriggers = [];
  let savedReturn;
  try { savedReturn = JSON.parse(sessionStorage.getItem('eli-project-return') || 'null'); } catch (_) {}

  function track(tween) {
    running.add(tween);
    tween.eventCallback('onComplete', () => running.delete(tween));
    tween.eventCallback('onInterrupt', () => running.delete(tween));
    return tween;
  }
  function settle(element) {
    gsap.killTweensOf(element);
    gsap.set(element, {clearProps:'opacity,transform,clipPath'});
    if (element.matches('.technology-row')) {
      const parts=element.querySelectorAll('dt,dd'); gsap.killTweensOf(parts); gsap.set(parts,{clearProps:'opacity,transform,clipPath'});
    }
    if (element.matches('.archive-list li')) {
      const parts=element.querySelectorAll('.archive-title-group,.archive-summary,.archive-arrow');
      gsap.killTweensOf(parts); gsap.set(parts,{clearProps:'opacity,transform,clipPath'});
    }
  }
  function finishFilter() {
    const pending = filterTween;
    filterTween = null;
    pending?.progress(1);
    pending?.kill();
    filtering = false;
    rows.forEach(settle);
  }
  function reveal(element, delay = 0) {
    if (finished.has(element)) return;
    finished.add(element);
    revealObserver?.unobserve(element);
    if (reduce.matches) { settle(element); return; }
    if (element.matches('.technology-row')) {
      const sequence=track(gsap.timeline({delay,defaults:{ease:'power3.out',clearProps:'opacity,transform,clipPath'}}));
      sequence.fromTo(element.querySelector('dt'),{x:20,clipPath:'inset(0 100% 0 0)'},{x:0,clipPath:'inset(0 0% 0 0)',duration:.5},0);
      sequence.fromTo(element.querySelector('dd'),{x:26,opacity:.2},{x:0,opacity:1,duration:.45},.06);
    } else if (element.matches('.technical-flow li')) {
      track(gsap.fromTo(element,{x:22,opacity:.25},{x:0,opacity:1,duration:.42,delay,ease:'power3.out',clearProps:'opacity,transform'}));
    } else if (element.matches('.archive-list li')) {
      const sequence=track(gsap.timeline({delay,defaults:{ease:'power3.out',clearProps:'opacity,transform,clipPath'}}));
      sequence.fromTo(element.querySelector('.archive-title-group'),{x:40,clipPath:'inset(0 100% 0 0)'},
        {x:0,clipPath:'inset(0 0% 0 0)',duration:.64},0);
      sequence.fromTo(element.querySelector('.archive-summary'),{opacity:0,x:24},{opacity:1,x:0,duration:.46},.13);
      sequence.fromTo(element.querySelector('.archive-arrow'),{opacity:0,x:-14},{opacity:1,x:0,duration:.35},.2);
    } else {
      track(gsap.fromTo(element, {opacity:0,y:24}, {opacity:1,y:0,
        duration:timing.reveal, delay, ease:'power3.out', overwrite:'auto', clearProps:'opacity,transform'}));
    }
  }

  // Each object has one owner. A list row, not the whole list, is the reveal unit.
  const revealElements = [
    ...document.querySelectorAll('.participation-modes>div,.fde-lead,.fde-principles>div,.case-facts>div,.detail-content>section:not(#technical),.contact-section>div,.technology-row,.capability-card,.technical-flow li,.about-question'),
    ...rows
  ];
  if ('IntersectionObserver' in window) {
    revealObserver = new IntersectionObserver(entries => {
      const incoming = entries.filter(entry=>entry.isIntersecting && !entry.target.hidden && !finished.has(entry.target));
      if (filtering) return;
      incoming.forEach((entry,index)=>reveal(entry.target, Math.min(index,3)*.045));
    }, {threshold:.08,rootMargin:'0px 0px -12px 0px'});
    revealElements.forEach(element=>revealObserver.observe(element));
  }

  const title = main.querySelector('h1');
  const nativeNavigation = 'onpageswap' in window && 'onpagereveal' in window;
  document.documentElement.dataset.nativeNavigation=String(nativeNavigation);
  const sharedIncoming = nativeNavigation && main.classList.contains('detail-main') &&
    document.referrer.startsWith(location.origin) && new URL(document.referrer).pathname.endsWith('/records.html');
  let titleContent;
  if (title) {
    titleContent = document.createElement('span');
    titleContent.className = 'editorial-title-content';
    titleContent.append(...title.childNodes);
    title.append(titleContent);
    title.classList.add('editorial-title-mask');
  }
  const isReturning = new URLSearchParams(location.search).has('return') || location.hash.startsWith('#project-') || performance.getEntriesByType('navigation')[0]?.type === 'back_forward';
  const replayPageHeading = main.classList.contains('about-main') || main.classList.contains('records-main');
  // Keep the reader's optional detail on this history entry when returning from a case.
  const aboutQuestions = [...main.querySelectorAll('.about-question')];
  function saveAboutQuestions() {
    if (!aboutQuestions.length) return;
    try {
      history.replaceState({...history.state,eliAboutQuestions:aboutQuestions.flatMap((question,index)=>question.open ? [index] : [])},'');
    } catch (_) {}
  }
  if (aboutQuestions.length) {
    const savedQuestions=history.state?.eliAboutQuestions;
    if (isReturning && Array.isArray(savedQuestions)) {
      savedQuestions.forEach(index=> { if (Number.isInteger(index) && aboutQuestions[index]) aboutQuestions[index].open=true; });
    } else if (Array.isArray(savedQuestions)) saveAboutQuestions();
    aboutQuestions.forEach(question=>question.addEventListener('toggle',saveAboutQuestions));
    main.querySelectorAll('#questions a').forEach(link=>link.addEventListener('click',saveAboutQuestions));
  }
  // A finite visual explanation, with no timers or moving hit areas.
  const fdeMap=main.querySelector('[data-fde-map]');
  const mapNodes=fdeMap?[...fdeMap.querySelectorAll('.fde-map-node')]:[];
  const mapReplay=fdeMap?.querySelector('.fde-map-replay');
  let mapMotion;
  function playMap() {
    mapMotion?.kill();
    if (!fdeMap) return;
    mapReplay.hidden=reduce.matches;
    if (reduce.matches) {
      fdeMap.dataset.mapStep='0';
      gsap.set(fdeMap.querySelectorAll('.fde-node-symbol,.fde-map-link>span,.fde-core-ring'),{clearProps:'transform,opacity'});
      return;
    }
    fdeMap.dataset.mapStep='0';
    mapMotion=track(gsap.timeline({defaults:{ease:'power2.out',clearProps:'transform,opacity'}}));
    mapNodes.forEach((node,index)=> {
      const at=index*.8;
      mapMotion.call(()=>{fdeMap.dataset.mapStep=String(index+1);},null,at);
      mapMotion.fromTo(node.querySelector('.fde-node-symbol'),{scale:.94,opacity:.65},{scale:1,opacity:1,duration:.55,immediateRender:false},at);
    });
    fdeMap.querySelectorAll('.fde-map-link>span').forEach((line,index)=> {
      mapMotion.fromTo(line,{scaleX:0},{scaleX:1,duration:.55,immediateRender:false},.3+index*.8);
    });
    mapMotion.fromTo(fdeMap.querySelector('.fde-core-ring-outer'),{rotation:-45},{rotation:0,duration:1.6,immediateRender:false},.45);
  }
  mapReplay?.addEventListener('click',playMap);
  let entrance, navigationTransition;
  function playEntrance() {
    finishEntrance();
    // These page headings keep their entry motion on repeat visits. Case returns
    // still preserve the shared project title and the saved reading context.
    if (reduce.matches || (isReturning && !replayPageHeading)) return;
    entrance = track(gsap.timeline({defaults:{ease:'power3.out',clearProps:'opacity,transform,clipPath,filter'}}));
    // Crisp title slide. One title owner also settles on the first input,
    // so the decorative reveal never delays a link or a screenshot control.
    if (titleContent && !sharedIncoming) entrance.fromTo(titleContent,
      {y:22,opacity:.15},
      {y:0,opacity:1,duration:timing.title},0);
    const sub = main.querySelector('.about-opening-intro,.records-heading>p:last-child,.detail-intro');
    if (sub) entrance.from(sub,{opacity:0,y:18,duration:.48},.18);
    if (fdeMap) entrance.from(fdeMap,{opacity:0,y:16,duration:.55},.16);
    // Animate the artwork, keeping its link's hit area stable from the first
    // frame. A clipped/moving link can lose its click between down and up.
    const image = main.querySelectorAll('.case-hero .detail-image-visual,.case-hero .detail-image figcaption');
    if (image.length) entrance.from(image,{opacity:0,y:24,clipPath:'inset(0 100% 0 0)',duration:.8},sharedIncoming ? .24 : .12);
  }
  playEntrance();
  playMap();
  function finishEntrance() {
    const pending=entrance;
    entrance=null;
    pending?.progress(1);
    pending?.kill();
  }
  function finishInteractionEntrance() {
    // Once the reader acts, settle the shared title too so its snapshot cannot
    // float above a newly opened screenshot dialog.
    navigationTransition?.skipTransition();
    finishEntrance();
  }
  main.addEventListener('pointerdown',finishInteractionEntrance,true);
  main.addEventListener('keydown',finishInteractionEntrance,true);
  main.addEventListener('focusin',finishEntrance);

  window.PortfolioMotion = {
    filterCards(cards, apply) {
      finishFilter();
      if (follow) { gsap.killTweensOf(follow); gsap.set(follow,{opacity:0}); followTarget=null; rows.forEach(row=>row.classList.remove('archive-selected')); }
      cards.forEach(settle);
      if (reduce.matches || !Flip) { apply(); syncCategory?.(); return; }
      filtering = true;
      // Retain on-screen identity. A project far below the fold should enter at
      // its new position, not fly several thousand pixels across the viewport.
      const previousVisible = cards.filter(card=> {
        if (card.hidden) return false;
        const rect=card.getBoundingClientRect();
        return rect.top<innerHeight && rect.bottom>0;
      });
      const state = Flip.getState(previousVisible);
      apply();
      syncCategory?.();
      const visible = cards.filter(card=>!card.hidden);
      const hasRetained=visible.some(card=>previousVisible.includes(card));
      visible.forEach(card=> {
        const rect=card.getBoundingClientRect();
        if (rect.top<innerHeight && rect.bottom>0) finished.add(card);
      });
      const incoming=visible.filter(card=>!previousVisible.includes(card) && card.getBoundingClientRect().top<innerHeight);
      filterTween=gsap.timeline({onComplete:()=> {
        filterTween=null; filtering=false;
        visible.forEach(card=> { if (!finished.has(card)) { revealObserver?.unobserve(card); revealObserver?.observe(card); } });
      }});
      filterTween.add(Flip.from(state,{targets:visible,duration:timing.change,ease:'power3.inOut',scale:false,prune:true}),0);
      incoming.slice(0,6).forEach((card,index)=> {
        filterTween.fromTo(card,{opacity:0,x:48,clipPath:'inset(0 100% 0 0)'},
          {opacity:1,x:0,clipPath:'inset(0 0% 0 0)',duration:.4,ease:'power3.out',clearProps:'opacity,transform,clipPath'},
          (hasRetained ? .06 : 0)+index*.035);
      });
    }
  };
  // The selection surface follows intent, never the cursor coordinates.
  const archiveList=document.querySelector('.archive-list');
  const finePointer=matchMedia('(hover:hover) and (pointer:fine)');
  let follow, followTarget;
  if (archiveList && finePointer.matches) {
    follow=document.createElement('div');
    follow.className='archive-follow'; follow.setAttribute('aria-hidden','true');
    const surface=document.createElement('div'); surface.className='archive-surface';
    archiveList.before(surface); surface.append(follow,archiveList);
    const pointTo=row=> {
      if (row.hidden || reduce.matches || filtering) return;
      followTarget=row;
      rows.forEach(item=>item.classList.toggle('archive-selected',item===row));
      const listRect=archiveList.getBoundingClientRect(), rect=row.getBoundingClientRect();
      gsap.to(follow,{x:rect.left-listRect.left,y:rect.top-listRect.top,width:rect.width,height:rect.height,opacity:1,duration:.26,ease:'power3.out',overwrite:true});
    };
    rows.forEach(row=> {
      row.addEventListener('pointerenter',()=>pointTo(row));
      row.addEventListener('focusin',()=> { finishFilter(); settle(row); pointTo(row); });
    });
    archiveList.addEventListener('pointerleave',()=> {
      const focused=rows.find(row=>row.contains(document.activeElement));
      if (focused) { pointTo(focused); return; }
      followTarget=null; rows.forEach(row=>row.classList.remove('archive-selected'));
      gsap.to(follow,{opacity:0,duration:.12,overwrite:true});
    });
    archiveList.addEventListener('focusout',event=> {
      if (!archiveList.contains(event.relatedTarget)) {
        followTarget=null; rows.forEach(row=>row.classList.remove('archive-selected'));
        gsap.to(follow,{opacity:0,duration:.12,overwrite:true});
      }
    });
    addEventListener('resize',()=> { if(followTarget) pointTo(followTarget); });
  }
  // The selected category keeps its identity as it moves between controls.
  const filters=document.querySelector('.filters');
  const categoryButtons=filters?[...filters.querySelectorAll('button')]:[];
  let categoryMarker;
  if (filters && categoryButtons.length) {
    categoryMarker=document.createElement('span'); categoryMarker.className='category-marker';
    categoryMarker.setAttribute('aria-hidden','true'); filters.prepend(categoryMarker);
    syncCategory=(instant=false)=> {
      const selected=categoryButtons.find(button=>button.getAttribute('aria-pressed')==='true');
      if (!selected) return;
      const container=filters.getBoundingClientRect(), rect=selected.getBoundingClientRect();
      const position={x:rect.left-container.left+filters.scrollLeft,y:rect.top-container.top+filters.scrollTop,width:rect.width,height:rect.height};
      gsap.killTweensOf(categoryMarker);
      if (instant || reduce.matches) gsap.set(categoryMarker,position);
      else gsap.to(categoryMarker,{...position,duration:.24,ease:'power3.out',overwrite:true});
      categoryMarker.dataset.category=selected.dataset.filter;
    };
    syncCategory(true); filters.classList.add('filters-enhanced');
    categoryButtons.forEach(button=>button.addEventListener('click',()=>syncCategory()));
    document.querySelector('.reset-search')?.addEventListener('click',()=>syncCategory());
    addEventListener('resize',()=>syncCategory(true));
    document.fonts?.ready.then(()=>syncCategory(true));
  }
  const search = document.querySelector('#search');
  // Immediate search can interrupt a category transition without leaving ghosts.
  search?.addEventListener('input',finishFilter,true);
  document.querySelector('.reset-search')?.addEventListener('click',finishFilter,true);

  function updateReading() {
    scrollFrame=0;
    const extent=document.documentElement.scrollHeight-innerHeight;
    document.documentElement.style.setProperty('--reading-progress',String(extent>0?Math.min(1,scrollY/extent):0));
  }
  function scheduleReading() { if (!scrollFrame) scrollFrame=requestAnimationFrame(updateReading); }
  addEventListener('scroll',scheduleReading,{passive:true});
  addEventListener('resize',scheduleReading);
  scheduleReading();

  // The workflow retains its scroll feedback; optional detail stays native.
  const workflow=document.querySelector('[data-workflow]');
  const steps=workflow?[...workflow.querySelectorAll('.fde-cycle>li')]:[];
  let activeStep=-1;
  function chooseStep(index) {
    if (activeStep===index) return;
    activeStep=index;
    steps.forEach((step,i)=>step.classList.toggle('workflow-active',i===index));
    const position=workflow?.querySelector('.workflow-position>span');
    if (position) {
      position.textContent=String(index+1).padStart(2,'0');
      if (!reduce.matches) gsap.fromTo(position,{y:5,opacity:.5},{y:0,opacity:1,duration:.18,ease:'power2.out',overwrite:true,clearProps:'opacity,transform'});
    }
    if (workflow) workflow.dataset.activeStep=String(index+1);
  }
  function buildWorkflow() {
    workflowTriggers.forEach(trigger=>trigger.kill()); workflowTriggers=[];
    activeStep=-1;
    if (!workflow || ['stepper','route'].includes(workflow.dataset.component) || !ScrollTrigger || reduce.matches) {
      workflow?.classList.remove('workflow-enhanced');
      steps.forEach(step=>step.classList.remove('workflow-active'));
      return;
    }
    workflow.classList.add('workflow-enhanced');
    chooseStep(0);
    const progress=gsap.quickSetter(workflow.querySelector('.workflow-progress>span'),'scaleX');
    workflowTriggers.push(ScrollTrigger.create({trigger:steps[0],endTrigger:steps[steps.length-1],
      start:'top 55%',end:'bottom 55%',onUpdate:self=>progress(self.progress)}));
    steps.forEach((step,index)=>workflowTriggers.push(ScrollTrigger.create({trigger:step,
      start:'top 55%',end:'bottom 55%',onEnter:()=>chooseStep(index),onEnterBack:()=>chooseStep(index)})));
  }
  buildWorkflow();
  main.addEventListener('toggle', event => {
    if (event.target.matches('.about-disclosure')) ScrollTrigger?.refresh();
  }, true);
  document.fonts?.ready.then(()=>ScrollTrigger?.refresh());
  document.querySelectorAll('img').forEach(image=> {
    if (!image.complete) image.addEventListener('load',()=>ScrollTrigger?.refresh(),{once:true});
  });

  const caseLinks=[...document.querySelectorAll('.case-index a')];
  let indexObserver;
  if (caseLinks.length && 'IntersectionObserver' in window) {
    indexObserver=new IntersectionObserver(entries=> {
      const visible=entries.find(entry=>entry.isIntersecting);
      if (!visible) return;
      caseLinks.forEach(link=>link.hash==='#'+visible.target.id ? link.setAttribute('aria-current','location') : link.removeAttribute('aria-current'));
    },{rootMargin:'-5% 0px -65% 0px'});
    caseLinks.forEach(link=> {const section=document.getElementById(link.hash.slice(1));if(section)indexObserver.observe(section);});
  }

  // Cross-document title continuity is progressive enhancement, not a SPA router.
  const caseTitle=document.querySelector('.detail-header [data-project-title]');
  if (caseTitle) caseTitle.style.viewTransitionName='project-title';
  rows.forEach(row=> {
    const link=row.querySelector('a'), label=row.querySelector('[data-project-title]');
    link.addEventListener('pointerdown',event=> {
      if (!filtering || event.button!==0) return;
      // Keep the pressed object as the mouse-up target while an interrupted
      // FLIP settles. Otherwise a moving row can slide out from under the click.
      link.setPointerCapture?.(event.pointerId);
      finishFilter();
    });
    link.addEventListener('click',event=> {
      if (event.metaKey||event.ctrlKey||event.shiftKey||event.altKey) return;
      finishFilter();
      if (!reduce.matches) label.style.viewTransitionName='project-title';
    });
  });
  // Navigation owns the return URL/session. Motion only restores reading
  // position and the shared title for that verified list context.
  function restorePosition(cleanURL = false) {
    if (!savedReturn || !rows.length) return;
    const url=new URL(location.href);
    const requested=url.searchParams.get('return') || (url.hash.startsWith('#project-') ? url.hash.slice(9) : '');
    url.searchParams.delete('return');
    let source;
    try { source=new URL(savedReturn.source,location.origin); } catch (_) { return; }
    const context=new URL(url);
    source.searchParams.delete('pv');context.searchParams.delete('pv');
    if (requested!==savedReturn.id || source.origin!==location.origin ||
        source.pathname+source.search!==context.pathname+context.search) return;
    // Keep a clean source URL. A fragment would let browser or host scroll
    // restoration override the saved reading position after the transition.
    if (cleanURL) history.replaceState(null,'',url.pathname+url.search);
    const returningRow=document.getElementById('project-'+savedReturn.id);
    const returningTitle=returningRow?.querySelector('[data-project-title]');
    if (returningTitle && !reduce.matches) returningTitle.style.viewTransitionName='project-title';
    scrollTo({top:savedReturn.scroll,behavior:'instant'});
    returningRow?.classList.add('archive-returned');
    returningRow?.querySelector('a').focus({preventScroll:true});
  }
  window.addEventListener('pagereveal',event=> {
    if (!event.viewTransition) return;
    if (!sharedIncoming && !(rows.length && isReturning)) { event.viewTransition.skipTransition(); return; }
    navigationTransition=event.viewTransition;
    document.documentElement.dataset.routeMotion='native-title';
    if (titleContent && !replayPageHeading) settle(titleContent);
    if (rows.length) restorePosition();
    event.viewTransition.finished.finally(()=> {
      if (navigationTransition===event.viewTransition) navigationTransition=null;
      rows.forEach(row=>row.querySelector('[data-project-title]')?.style.removeProperty('view-transition-name'));
    });
  });
  window.addEventListener('pageswap',()=>finishFilter());
  window.addEventListener('pageshow',event=> {
    rows.forEach(row=> {const label=row.querySelector('[data-project-title]');if(label)label.style.removeProperty('view-transition-name');});
    if(event.persisted) {
      if (replayPageHeading) playEntrance();
      playMap();
      buildWorkflow();
      revealElements.forEach(element=>{if(!finished.has(element))revealObserver?.observe(element);});
      caseLinks.forEach(link=>{const section=document.getElementById(link.hash.slice(1));if(section)indexObserver?.observe(section);});
    }
    restorePosition(true);scheduleReading();
  });
  restorePosition();
  document.addEventListener('focusin',event=>revealElements.forEach(element=> {
    if(element.contains(event.target)){finished.add(element);revealObserver?.unobserve(element);settle(element);}
  }));
  function finishAll() {
    if (follow) { gsap.killTweensOf(follow); gsap.set(follow,{opacity:0}); }
    finishFilter();running.forEach(tween=>{tween.progress(1);tween.kill();});running.clear();
    revealElements.forEach(settle);
    if(titleContent)settle(titleContent);
  }
  reduce.addEventListener('change',()=>{finishAll();syncCategory?.(true);buildWorkflow();playMap();});
  window.addEventListener('pagehide',()=> {
    finishAll();revealObserver?.disconnect();indexObserver?.disconnect();
    workflowTriggers.forEach(trigger=>trigger.kill());workflowTriggers=[];
    cancelAnimationFrame(scrollFrame);scrollFrame=0;
  });
})();
