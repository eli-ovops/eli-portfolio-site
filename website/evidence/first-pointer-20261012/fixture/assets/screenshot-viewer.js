(() => {
  'use strict';
  const english = document.documentElement.lang === 'en';
  const actualLabel = english ? 'Actual size' : '原尺寸';
  const links = [...document.querySelectorAll('[data-image-view]')];
  if (!links.length || typeof HTMLDialogElement === 'undefined') return;
  const dialog = document.createElement('dialog');
  dialog.className = 'screenshot-dialog';
  dialog.setAttribute('aria-labelledby','screenshot-title');
  dialog.innerHTML = english ? '<div class="screenshot-toolbar"><h2 id="screenshot-title"></h2><div><button type="button" data-view-size>Actual size</button><button type="button" data-view-close aria-label="Close screenshot">Close ×</button></div></div><figure class="screenshot-figure"><img alt=""></figure><p class="screenshot-note">Interface preview · switch to actual size for details</p>' : '<div class="screenshot-toolbar"><h2 id="screenshot-title"></h2><div><button type="button" data-view-size>原尺寸</button><button type="button" data-view-close aria-label="关闭截图">关闭 ×</button></div></div><figure class="screenshot-figure"><img alt=""></figure><p class="screenshot-note">脱敏界面截图 · 可切换原尺寸查看细节</p>';
  document.body.append(dialog);
  const image = dialog.querySelector('img');
  const title = dialog.querySelector('h2');
  const size = dialog.querySelector('[data-view-size]');
  const note = dialog.querySelector('.screenshot-note');
  const defaultNote = note.textContent;
  let opener;
  function fit() { delete dialog.dataset.actual; size.textContent=actualLabel; }
  links.forEach(link => link.addEventListener('click', event => {
    if (event.defaultPrevented || event.button > 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
    event.preventDefault();
    opener=link;
    fit();
    title.textContent=link.dataset.imageTitle;
    image.alt=link.dataset.imageTitle+(english ? ' interface screenshot' : '界面截图');
    image.src=link.href;
    note.textContent=link.dataset.imageNote
      ? link.dataset.imageNote+(english ? ' · switch to actual size for details' : ' · 可切换原尺寸查看细节')
      : defaultNote;
    dialog.showModal();
    if (window.gsap && !matchMedia('(prefers-reduced-motion: reduce)').matches) {
      window.gsap.fromTo(image,{opacity:0,y:8},{opacity:1,y:0,duration:0.2,clearProps:'opacity,transform'});
    }
  }));
  size.addEventListener('click',()=>{
    dialog.dataset.actual=dialog.dataset.actual ? '' : 'true';
    size.textContent=dialog.dataset.actual ? (english ? 'Fit to screen' : '适应屏幕') : actualLabel;
  });
  dialog.querySelector('[data-view-close]').addEventListener('click',()=>dialog.close());
  dialog.addEventListener('click',event=>{if(event.target===dialog)dialog.close();});
  dialog.addEventListener('close',()=>{
    window.gsap?.killTweensOf(image);
    image.style.opacity='';image.style.transform='';
    fit();
    opener?.focus({preventScroll:true});
  });
})();
