(() => {
  'use strict';
  const layer=document.querySelector('[data-home-ambient]');
  const control=document.querySelector('[data-ambient-control]');
  if (!layer || !control) return;
  const reduce=matchMedia('(prefers-reduced-motion: reduce)');
  const fine=matchMedia('(hover: hover) and (pointer: fine)');
  const english=document.documentElement.lang==='en';
  let userPaused=false, leaving=false, frame=0, point;
  try { userPaused=sessionStorage.getItem('eli-home-ambient-paused')==='true'; } catch (_) {}
  function resetPointer() {
    cancelAnimationFrame(frame);frame=0;
    layer.style.removeProperty('--ambient-x');layer.style.removeProperty('--ambient-y');
  }
  function sync() {
    const active=!reduce.matches && !userPaused && !document.hidden && !leaving;
    layer.dataset.active=String(active);
    control.hidden=false;
    control.disabled=reduce.matches;
    control.setAttribute('aria-pressed',String(!reduce.matches && !userPaused));
    control.title=reduce.matches ? (english?'Reduced motion follows your system setting':'已按系统设置减少动态')
      : userPaused ? (english?'Play background motion':'播放背景动效') : (english?'Pause background motion':'暂停背景动效');
    if (!active || !fine.matches) resetPointer();
  }
  control.addEventListener('click',()=> {
    if (reduce.matches) return;
    userPaused=!userPaused;
    try { sessionStorage.setItem('eli-home-ambient-paused',String(userPaused)); } catch (_) {}
    sync();
  });
  addEventListener('pointermove',event=> {
    if (event.pointerType!=='mouse' || !fine.matches || layer.dataset.active!=='true') return;
    point={x:event.clientX,y:event.clientY};
    if (frame) return;
    frame=requestAnimationFrame(()=> {
      frame=0;
      layer.style.setProperty('--ambient-x',((point.x/innerWidth-.5)*12).toFixed(2)+'px');
      layer.style.setProperty('--ambient-y',((point.y/innerHeight-.5)*8).toFixed(2)+'px');
    });
  },{passive:true});
  document.documentElement.addEventListener('pointerleave',resetPointer);
  reduce.addEventListener('change',sync);fine.addEventListener('change',sync);
  document.addEventListener('visibilitychange',sync);
  addEventListener('pagehide',()=>{leaving=true;sync();});
  addEventListener('pageshow',()=>{leaving=false;sync();});
  sync();
})();
