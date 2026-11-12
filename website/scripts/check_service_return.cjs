'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm'),path=require('node:path');
const source=fs.readFileSync(process.argv[2]||path.join(__dirname,'../assets/page-version.js'),'utf8');
const revision='1234567890abcdef1234';
function casePage(prefix,from,{stateSource,referrer}={}) {
 const location=new URL('https://site.test'+prefix+'cases/p10.html');
 if(from)location.searchParams.set('from',from);
 const back={href:'https://site.test'+prefix+'records.html',textContent:'← 返回项目库'};
 const related={href:'https://site.test'+prefix+'cases/p09.html'};
 const history={state:{reader:42,...(stateSource?{eliProjectReturnSource:stateSource}:{})},replaceState(s){this.state=s;}};
 const events={};
 const document={documentElement:{lang:prefix.includes('/en/')?'en':'zh-CN'},referrer:referrer||'',currentScript:{src:'https://site.test'+prefix.replace(/en\/$/,'')+'assets/page-version.js'},querySelector(s){return s.includes('portfolio-revision')?{content:revision}:s==='.back'?back:{dataset:{projectTitle:'P10'}};},querySelectorAll(s){return s==='.case-related a'?[related]:[back,related];},addEventListener(){}};
 vm.runInNewContext(source,{URL,location,history,document,addEventListener(n,fn){events[n]=fn;},sessionStorage:{getItem(){return null;}}});
 events.pageshow?.(); // BFCache must be idempotent after .back has been rewritten.
 return {back:new URL(back.href,location),label:back.textContent,related:new URL(related.href,location),history};
}
function serviceClick(prefix,slug,proof) {
 const location=new URL('https://site.test'+prefix+'services/'+slug+'.html?pv=old');
 const link={href:'https://site.test'+prefix+'cases/p10.html',closest(s){return s==='#service-proof'&&proof?{}:null;}};
 const events={};const history={state:{},replaceState(){}};
 const document={currentScript:{src:'https://site.test'+prefix.replace(/en\/$/,'')+'assets/page-version.js'},querySelector(){return {content:revision};},querySelectorAll(){return [link];},addEventListener(n,fn){events[n]=fn;}};
 vm.runInNewContext(source,{URL,location,history,document,addEventListener(){},sessionStorage:{setItem(){throw Error('Service must not overwrite catalogue session');}}});
 events.click({target:{closest:()=>link}});
 return new URL(link.href,location);
}
for(const prefix of ['/','/en/','/sites/portfolio/','/sites/portfolio/en/']) {
 for(const slug of ['fde-consulting','ai-agent','workflow-automation']) {
  for(const hash of ['#service-proof','#cases']) {
   const origin=prefix+'services/'+slug+'.html?pv=old'+hash;
   for(const options of [{from:origin},{stateSource:origin},{referrer:'https://site.test'+origin}]) {
    const out=casePage(prefix,options.from,options);
    assert.equal(out.back.pathname,prefix+'services/'+slug+'.html','case must return to the service');
    assert.equal(out.back.hash,hash);assert.equal(out.back.searchParams.has('pv'),false);
    assert.equal(out.history.state.reader,42);
    assert.equal(new URL(out.related.searchParams.get('from'),'https://site.test').pathname,out.back.pathname);
    const second=casePage(prefix,out.related.searchParams.get('from'));
    assert.equal(second.back.pathname,out.back.pathname,'related case must retain service origin');
    assert.match(out.label,/服务|service/);
   }
  }
  const clicked=serviceClick(prefix,slug,true);const origin=new URL(clicked.searchParams.get('from'),'https://site.test');
  assert.equal(origin.pathname,prefix+'services/'+slug+'.html');assert.equal(origin.hash,'#service-proof');
  assert.equal(new URL(serviceClick(prefix,slug,false).searchParams.get('from'),'https://site.test').hash,'#cases');
 }
}
for(const bad of ['https://evil.test/services/fde-consulting.html','/en/services/fde-consulting.html','/services/unknown.html','/services/../about.html']) {
 assert.equal(casePage('/',bad).back.pathname,'/records.html');
}
const cleaned=casePage('/','/services/ai-agent.html?q=stale&category=old#nonsense');
assert.equal(cleaned.back.searchParams.has('q'),false);assert.equal(cleaned.back.searchParams.has('category'),false);assert.equal(cleaned.back.hash,'#cases');
console.log('PASS: service entry, related chain, BFCache/history/referrer, bilingual/subpath origins, catalogue isolation and invalid sources');
