/* Exercise both real controllers: an old list session must not rewrite a
 * homepage case's return, while explicit and historical origins stay usable. */
'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm'),path=require('node:path');
const root=process.argv[2] || path.join(__dirname,'..');
const navigation=fs.readFileSync(path.join(root,'assets/page-version.js'),'utf8');
const editorial=fs.readFileSync(path.join(root,'assets/editorial.js'),'utf8');
const revision='1234567890abcdef1234';
function run(prefix,{from,referrer,storedSource,stateSource}={}) {
  const noop=()=>{},events={};
  const location=new URL('http://example.test'+prefix+'cases/p10.html');
  if(from)location.searchParams.set('from',from);
  const back={href:'../records.html'};
  const title={dataset:{projectTitle:'P10'},style:{removeProperty:noop}};
  const main={classList:{contains:()=>false},querySelector:()=>null,querySelectorAll:()=>[],addEventListener:noop};
  const style={setProperty:noop,removeProperty:noop};
  const document={referrer:referrer || 'http://example.test'+prefix+'index.html',
    documentElement:{dataset:{},classList:{add:noop},style,scrollHeight:720},
    currentScript:{src:'http://example.test'+prefix.replace(/en\/$/,'')+'assets/page-version.js'},
    querySelector(selector){return selector==='main'?main:selector==='.back'?back:
      selector.includes('portfolio-revision')?{content:revision}:
      selector==='.detail-header [data-project-title]'?title:null;},
    querySelectorAll:()=>[],addEventListener:noop};
  const history={state:{reader:'retain',...(stateSource?{eliProjectReturnSource:stateSource}:{})},
    replaceState(state,_,url){this.state=state;if(url)location.href=new URL(url,location).href;}};
  const session=JSON.stringify({source:storedSource || prefix+'records.html?category=Client+work&q=inventory',id:'p10',scroll:220});
  const context={URL,URLSearchParams,location,history,document,innerHeight:720,scrollY:0,
    sessionStorage:{getItem:()=>session},matchMedia:()=>({matches:true,addEventListener:noop}),
    performance:{getEntriesByType:()=>[{type:'navigate'}]},requestAnimationFrame:()=>1,cancelAnimationFrame:noop,
    addEventListener(type,fn){(events[type] ||= []).push(fn);},scrollTo:noop};
  context.window={gsap:{version:'test',registerPlugin:noop,killTweensOf:noop,set:noop},addEventListener:context.addEventListener};
  vm.runInNewContext(navigation,context);vm.runInNewContext(editorial,context);
  for(const handler of events.pageshow || [])handler({persisted:false});
  return {back:new URL(back.href,location),history};
}
for(const prefix of ['/','/en/','/sites/portfolio/','/sites/portfolio/en/']) {
  const stale=prefix+'records.html?category=Client+work&q=inventory';
  const direct=run(prefix,{storedSource:stale});
  assert.equal(direct.back.searchParams.has('q'),false,'homepage must not resurrect a cleared query');
  assert.equal(direct.back.searchParams.has('category'),false);
  // An older case retains its actual explicit origin despite a newer session.
  const origin=prefix+'records.html?category=Client+work&q=old-search&return=p10';
  for(const options of [{from:origin},{stateSource:origin}]) {
    const result=run(prefix,{...options,storedSource:stale});
    assert.equal(result.back.searchParams.get('q'),'old-search');
    assert.equal(result.back.searchParams.get('return'),'p10');
    assert.equal(result.back.searchParams.has('pv'),false);
    assert.equal(result.history.state.reader,'retain');
  }
  const clearedReferrer=run(prefix,{storedSource:stale,referrer:'http://example.test'+prefix+'records.html'});
  assert.equal(clearedReferrer.back.searchParams.has('q'),false,'cleared list referrer must not borrow a stale session');
  const legacy=run(prefix,{storedSource:stale,referrer:'http://example.test'+stale});
  assert.equal(legacy.back.searchParams.get('q'),'inventory','matching legacy list origin remains compatible');
}
console.log('PASS: homepage/cleared origin stays clean; real explicit/history/legacy list origins retained in both controllers');
