'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm'),path=require('node:path');
const source=fs.readFileSync(path.join(__dirname,'../assets/page-version.js'),'utf8');
const revision='1234567890abcdef1234';
function casePage(prefix,from,referrer='') {
  const location=new URL('https://site.test'+prefix+'cases/p09.html');
  if(from)location.searchParams.set('from',from);
  const back={href:'https://site.test'+prefix+'records.html',textContent:'Back'};
  const related={href:'https://site.test'+prefix+'cases/p04.html'};
  const history={state:{reader:42},replaceState(s){this.state=s;}};
  const document={documentElement:{lang:prefix.includes('/en/')?'en':'zh-CN'},referrer,
    currentScript:{src:'https://site.test'+prefix.replace(/en\/$/,'')+'assets/page-version.js'},
    querySelector(s){return s.includes('portfolio-revision')?{content:revision}:s==='.back'?back:{dataset:{projectTitle:'P09'}};},
    querySelectorAll(s){return s==='.case-related a'?[related]:[back,related];},addEventListener(){}};
  vm.runInNewContext(source,{URL,location,history,document,addEventListener(){},sessionStorage:{getItem(){throw Error('Home must not borrow old catalogue state');}}});
  return {back:new URL(back.href,location),related:new URL(related.href,location),history};
}
function homeClick(prefix,home='index.html') {
  const location=new URL('https://site.test'+prefix+home+'?q=stale&category=old');
  const link={href:'https://site.test'+prefix+'cases/p36.html',closest(){return null;}};
  const events={};
  const document={currentScript:{src:'https://site.test'+prefix.replace(/en\/$/,'')+'assets/page-version.js'},querySelector(){return {content:revision};},querySelectorAll(){return [link];},addEventListener(n,f){events[n]=f;}};
  vm.runInNewContext(source,{URL,location,history:{state:{},replaceState(){}},document,addEventListener(){}});
  events.click({target:{closest:()=>link}});
  return new URL(link.href,location);
}
for(const prefix of ['/','/en/','/sites/portfolio/','/sites/portfolio/en/']) {
  for(const home of ['index.html','']) {
    const clicked=homeClick(prefix,home);
    assert.ok(clicked.searchParams.get('from'),'home case links must carry their source');
    const result=casePage(prefix,clicked.searchParams.get('from'));
    assert.equal(result.back.pathname,prefix);
    assert.equal(result.back.hash,'#work');
    assert.equal(result.back.searchParams.get('project'),'p36','related case must preserve the selected homepage project');
    assert.equal(result.back.searchParams.has('pv'),false);
    assert.equal(result.back.searchParams.has('q'),false);
    assert.equal(result.back.searchParams.has('category'),false);
    assert.equal(result.history.state.reader,42);
    const second=casePage(prefix,result.related.searchParams.get('from'));
    assert.equal(second.back.href,result.back.href);
    const fallback=casePage(prefix,null,'https://site.test'+prefix+home);
    assert.equal(fallback.back.pathname,prefix);
    assert.equal(fallback.back.hash,'#work');
  }
}
for(const from of ['https://evil.test/index.html','/en/index.html?project=p36','/not-home.html','/services/unknown.html']) {
  assert.equal(casePage('/',from).back.pathname,'/records.html');
}
console.log('PASS: homepage/root entry, related origin, project selection, no stale filters, bilingual/subpath boundaries');
