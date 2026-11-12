(() => {
  'use strict';
  const gsap = window.gsap;
  const reduce = matchMedia('(prefers-reduced-motion: reduce)');
  const elements = [...document.querySelectorAll('.case-hero .detail-image,.case-facts>div,.detail-content>section,.participation-modes>div')];
  const tweens = new Set();
  const reveal = element => {
    gsap?.killTweensOf(element);
    gsap?.set(element, {clearProps:'opacity,transform'});
  };
  if (gsap && 'IntersectionObserver' in window) {
    const observer = new IntersectionObserver(entries => entries.forEach(entry => {
      if (!entry.isIntersecting) return;
      observer.unobserve(entry.target);
      reveal(entry.target);
      if (reduce.matches) return;
      const tween = gsap.fromTo(entry.target, {opacity:0,y:20}, {opacity:1,y:0,duration:.65,
        ease:'power3.out',clearProps:'opacity,transform',onComplete:()=>tweens.delete(tween)});
      tweens.add(tween);
    }), {threshold:.06});
    elements.forEach(element => {
      if (!reduce.matches && !location.hash) gsap.set(element,{opacity:0});
      observer.observe(element);
    });
    document.addEventListener('focusin', event => elements.forEach(element => {
      if (element.contains(event.target)) { observer.unobserve(element); reveal(element); }
    }));
    const finish = () => { tweens.forEach(tween=>tween.kill()); tweens.clear(); elements.forEach(reveal); };
    reduce.addEventListener('change',finish);
    window.addEventListener('pagehide',()=>{observer.disconnect();finish();});
  }
  const links = [...document.querySelectorAll('.case-index a')];
  if (links.length && 'IntersectionObserver' in window) {
    const sections = links.map(link=>document.getElementById(link.hash.slice(1))).filter(Boolean);
    const current = new IntersectionObserver(entries=> {
      const entry=entries.find(item=>item.isIntersecting);
      if (!entry) return;
      links.forEach(link=>link.hash==='#'+entry.target.id ? link.setAttribute('aria-current','location') : link.removeAttribute('aria-current'));
    },{rootMargin:'-5% 0px -65% 0px'});
    sections.forEach(section=>current.observe(section));
    window.addEventListener('pagehide',()=>current.disconnect());
  }
})();
