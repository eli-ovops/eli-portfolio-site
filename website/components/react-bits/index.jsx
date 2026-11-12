import React from 'react';
import { createRoot } from 'react-dom/client';
import FlexCarousel from './components/FlexCarousel.jsx';

// Website integration only. FlexCarousel.jsx and its CSS match the registry byte for byte.
const stage = document.querySelector('[data-depth-stage]');
if (stage) {
  const section = stage.closest('.selected-work');
  const gallery = stage.querySelector('[data-gallery]');
  const cards = [...gallery.querySelectorAll('.gallery-project')];
  const english = document.documentElement.lang === 'en';
  const reduce = matchMedia('(prefers-reduced-motion: reduce)');
  const mobile = matchMedia('(max-width: 650px)');
  const controls = stage.querySelector('.depth-controls');
  const label = controls.querySelector('.depth-position');
  const previous = controls.querySelector('[data-depth-prev]');
  const next = controls.querySelector('[data-depth-next]');
  const projectId = card => card.querySelector('.project-process[id]').id.replace('process-', '');
  const returning = performance.getEntriesByType('navigation')[0]?.type === 'back_forward';
  const saved = returning ? history.state?.portfolioGallery : null;
  const requested = new URL(location.href).searchParams.get('project');
  const initialId = saved?.selected?.replace('process-', '') || requested;
  let active = Math.max(0, cards.findIndex(card => projectId(card) === initialId));
  let localActive = 0, commanded = 0, pending = null, renderer = null;
  const host = document.createElement('div');
  host.className = 'official-flex-shell'; host.dataset.componentState = 'loading';
  stage.insertBefore(host, controls);
  const nav = document.createElement('nav'); nav.className = 'flex-carousel-index';
  nav.setAttribute('aria-label', english ? 'Choose a project' : '快速选择项目');
  controls.querySelector('[data-depth-hint]').replaceWith(nav);
  const items = cards.map((card, index) => ({
    src: card.querySelector('.project-image img')?.src || card.querySelector('.project-image').href,
    alt: card.querySelector('h3').textContent,
    title: card.dataset.galleryLabel || card.querySelector('h3').textContent,
    projectIndex:index
  }));
  let ordered = items.slice(active).concat(items.slice(0, active));
  function send(key) { renderer?.dispatchEvent(new KeyboardEvent('keydown', {key, cancelable:true})); }
  function goTo(index) {
    if (!renderer) return;
    const target = ordered.findIndex(item => item.projectIndex === index);
    let delta = (target - commanded + cards.length) % cards.length;
    if (delta > cards.length / 2) delta -= cards.length;
    pending = target; commanded = target;
    if (!delta) { send('Escape'); return; }
    for (let n = 0; n < Math.abs(delta); n++) send(delta > 0 ? 'ArrowRight' : 'ArrowLeft');
  }
  const buttons = cards.map((card, index) => {
    const button = document.createElement('button'); button.type = 'button';
    button.textContent = items[index].title;
    button.addEventListener('click', () => goTo(index)); nav.append(button);
    // Keep the site's original high-resolution viewer as a separate action.
    const source = card.querySelector('.project-image');
    const open = document.createElement('a'); open.className = 'text-link flex-full-image';
    open.href = source.href; open.dataset.imageView = '';
    open.dataset.imageTitle = source.dataset.imageTitle || card.querySelector('h3').textContent;
    open.dataset.imageAlt = source.dataset.imageAlt || open.dataset.imageTitle;
    open.dataset.imageNote = source.dataset.imageNote || '';
    open.setAttribute('aria-haspopup', 'dialog');
    open.textContent = english ? 'View image ↗' : '放大截图 ↗';
    card.querySelector('.selected-caption').append(open);
    const details = card.querySelector('.project-process');
    if (saved?.expanded) details.open = saved.expanded.includes(details.id);
    return button;
  });
  function activate(index, item) {
    active = item.projectIndex; localActive = index;
    if (pending === index) pending = null;
    if (pending === null) commanded = index;
    cards.forEach((card, i) => {
      const selected = i === active;
      card.classList.toggle('depth-current', selected); card.inert = !selected;
      card.setAttribute('aria-hidden', String(!selected));
      buttons[i].setAttribute('aria-pressed', String(selected));
    });
    label.textContent = `${String(active + 1).padStart(2, '0')} / ${String(cards.length).padStart(2, '0')}`;
    stage.dataset.depthPosition = String(active);
  }
  function fallback() {
    host.dataset.componentState = 'fallback'; host.hidden = true; controls.hidden = true;
    section.classList.remove('depth-enabled', 'flex-gallery-enabled', 'flex-official-enabled');
    cards.forEach(card => { card.inert = false; card.removeAttribute('aria-hidden'); });
    gallery.style.removeProperty('min-height');
  }
  class CarouselBoundary extends React.Component {
    state = {failed:false};
    static getDerivedStateFromError() { return {failed:true}; }
    componentDidCatch() { fallback(); }
    render() { return this.state.failed ? null : this.props.children; }
  }
  const root = createRoot(host);
  function OfficialCarousel() {
    React.useEffect(() => {
      // Old instances must not mark a new renderer as unsupported during a remount.
      const check = setTimeout(() => { if (!host.querySelector('canvas')) fallback(); }, 0);
      return () => clearTimeout(check);
    }, []);
    return <FlexCarousel
      items={ordered}
      preset="liquid"
      intro="rise"
      cardHeight={0.5}
      gap={12}
      squeeze={0.2}
      focusOnClick
      captions
      captureWheel={!mobile.matches}
      onChange={activate}
    />;
  }
  function render() {
    root.render(<CarouselBoundary><OfficialCarousel
      key={reduce.matches ? 'reduced' : 'motion'}
    /></CarouselBoundary>);
  }
  function measureCaptions() {
    if (!renderer) return;
    let minimum = 0;
    cards.forEach(card => {
      const copy = card.cloneNode(true); copy.classList.add('depth-current'); copy.inert = true;
      copy.setAttribute('aria-hidden','true'); copy.removeAttribute('id');
      copy.querySelectorAll('[id]').forEach(node => node.removeAttribute('id'));
      copy.querySelectorAll('details').forEach(details => {
        details.open = false; delete details.dataset.motionOpen; details.style.removeProperty('height');
      });
      copy.style.cssText = 'position:absolute;inset:auto;visibility:hidden;pointer-events:none;width:100%;';
      gallery.append(copy);
      minimum = Math.max(minimum, Math.ceil(copy.querySelector('.selected-caption').getBoundingClientRect().height));
      copy.remove();
    });
    gallery.style.minHeight = `${minimum}px`;
  }
  new MutationObserver(() => {
    const canvas = host.querySelector('canvas');
    if (!canvas) return;
    const container = canvas.closest('.flex-carousel');
    if (renderer === container) return;
    renderer = container; host.hidden = false; host.dataset.componentState = 'webgl2';
    renderer.setAttribute('aria-label', english ? 'Project images. Drag or click to focus.' : '项目图片，可拖动或点击聚焦');
    host.querySelector('.flex-carousel__live')?.setAttribute('aria-live','off');
    section.classList.add('depth-enabled', 'flex-gallery-enabled', 'flex-official-enabled');
    stage.dataset.component = 'react-bits-flex-carousel-official'; controls.hidden = false;
    canvas.addEventListener('webglcontextlost', () => {
      // Upstream intentionally releases the old context on unmount.
      if (canvas.isConnected && canvas === host.querySelector('canvas')) fallback();
    }, {once:true});
    renderer.addEventListener('pointerdown', () => { commanded = localActive; pending = null; }, {capture:true});
    renderer.addEventListener('wheel', () => { commanded = localActive; pending = null; }, {capture:true,passive:true});
    new ResizeObserver(measureCaptions).observe(host);
    measureCaptions();
  }).observe(host, {childList:true,subtree:true});
  previous.addEventListener('click', () => {
    const at = ordered[commanded].projectIndex; goTo((at + cards.length - 1) % cards.length);
  });
  next.addEventListener('click', () => {
    const at = ordered[commanded].projectIndex; goTo((at + 1) % cards.length);
  });
  stage.addEventListener('keydown', event => {
    if (event.target !== stage) return;
    if (['ArrowLeft','ArrowRight','Home','End','Enter','Escape',' '].includes(event.key)) {
      event.preventDefault(); send(event.key);
    }
  });
  reduce.addEventListener('change', () => {
    ordered = items.slice(active).concat(items.slice(0, active));
    localActive = commanded = 0; pending = null; renderer = null; render();
  });
  mobile.addEventListener('change', render);
  addEventListener('pagehide', () => {
    const expanded = cards.filter(card => {
      const d = card.querySelector('.project-process'); return d.dataset.motionOpen ? d.dataset.motionOpen === 'true' : d.open;
    }).map(card => card.querySelector('.project-process').id);
    history.replaceState({...history.state, portfolioGallery:{selected:'process-'+projectId(cards[active]), expanded, scrollY}},'');
  });
  document.fonts.ready.then(measureCaptions);
  render();
}
