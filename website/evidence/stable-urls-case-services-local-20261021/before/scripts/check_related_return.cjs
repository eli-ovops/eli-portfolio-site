"use strict";
const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm'),path=require('node:path');
const source=fs.readFileSync(process.argv[2] || path.join(__dirname,'../assets/page-version.js'),'utf8');
const revision='1234567890abcdef1234';
function runCase(prefix,id,origin) {
  const current=new URL('http://example.test'+prefix+'cases/'+id+'.html?from='+encodeURIComponent(origin));
  const back={href:'http://example.test'+prefix+'records.html'},related={href:'http://example.test'+prefix+'cases/p09.html'};
  const history={state:{reader:'keep'},replaceState(state){this.state=state;}};
  const document={currentScript:{src:'http://example.test'+prefix.replace(/en\/$/,'')+'assets/page-version.js'},
    querySelector(s){return s.includes('portfolio-revision') ? {content:revision} : s==='.back' ? back : {dataset:{projectTitle:id.toUpperCase()}};},
    querySelectorAll(s){return s==='.case-related a' ? [related] : [back,related];},addEventListener(){}};
  vm.runInNewContext(source,{URL,location:current,history,document,addEventListener(){},sessionStorage:{getItem(){return null;}}});
  return {back:new URL(back.href,current),related:new URL(related.href,current),history};
}
for(const prefix of ['/','/en/','/sites/portfolio/','/sites/portfolio/en/']) {
  const origin=prefix+'records.html?category=Client+work&q=inventory&return=p10';
  for(const id of ['p10','p09','p04']) {
    const result=runCase(prefix,id,origin);
    assert.equal(result.back.searchParams.get('q'),'inventory');
    assert.equal(result.back.searchParams.get('category'),'Client work');
    assert.equal(result.back.searchParams.get('return'),'p10');
    assert.equal(result.back.searchParams.get('pv'),revision);
    assert.equal(result.history.state.reader,'keep');
    assert.equal(new URL(result.related.searchParams.get('from'),'http://example.test').searchParams.get('return'),'p10');
  }
}
for(const origin of ['https://other.test/records.html?q=secret&return=p10','/en/records.html?q=wrong-language&return=p10','/records.html?q=missing-id']) {
  assert.equal(runCase('/','p04',origin).back.searchParams.has('q'),false);
}
console.log('PASS: related cases preserve list query/category/origin without GSAP; external/foreign-language/invalid origins ignored');
