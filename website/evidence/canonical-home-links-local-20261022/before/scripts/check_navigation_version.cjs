/* Regression: stable navigation preserves history/query/hash and legacy returns. */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const source = fs.readFileSync(path.join(__dirname,'../assets/page-version.js'),'utf8');
const revision = '1234567890abcdef1234';
function run(url, script, hrefs) {
  const location = new URL(url), state = {eliAboutQuestions:[1],portfolioGallery:{index:2}};
  const calls=[], events={}, links=hrefs.map(href=>({href:new URL(href,url).href}));
  const context={URL,location,history:{state,replaceState:(saved,_,address)=>{
      calls.push({saved,address}); if(address) location.href=new URL(address,location).href;
    }},
    document:{currentScript:{src:script},querySelector:()=>({content:revision}),querySelectorAll:()=>links,
      addEventListener:(event,fn)=>{events[event]=fn;}},addEventListener:(event,fn)=>{events[event]=fn;}};
  vm.runInNewContext(source,context);
  return {calls,links,state,events};
}
const result=run('http://example.test/sites/portfolio/records.html?pv=old&category=Client%20work&q=inventory&return=p10#project-p10',
  'http://example.test/sites/portfolio/assets/page-version.js?v=asset',
  ['cases/p10.html?pv=old','en/records.html?pv=old','#main','/login?pv=external-scope',
   'https://social.test/profile?pv=their-param','assets/image.png?v=asset']);
assert.equal(result.calls.length,1);
assert.equal(result.calls[0].saved,result.state);
const address=new URL(result.calls[0].address,'http://example.test');
assert.equal(address.searchParams.get('q'),'inventory');
assert.equal(address.searchParams.get('category'),'Client work');
assert.equal(address.searchParams.get('return'),'p10');
assert.equal(address.hash,'#project-p10');
assert.equal(address.searchParams.has('pv'),false);
for (const link of result.links.slice(0,3)) assert.equal(new URL(link.href,'http://example.test').searchParams.has('pv'),false);
assert.equal(result.links[3].href,'http://example.test/login?pv=external-scope');
assert.equal(result.links[4].href,'https://social.test/profile?pv=their-param');
assert.equal(result.links[5].href,'http://example.test/sites/portfolio/assets/image.png?v=asset');
result.events.pageshow(); assert.equal(result.calls.length,1,'BFCache cleanup is idempotent');
const english=run('http://example.test/sites/portfolio/en/cases/p10.html',
  'http://example.test/sites/portfolio/assets/page-version.js',['../../records.html']);
assert.equal(english.calls.length,0,'clean bilingual addresses stay unchanged');
assert.equal(new URL(english.links[0].href,'http://example.test').pathname,'/sites/portfolio/records.html');
const current=run('http://example.test/sites/portfolio/',
  'http://example.test/sites/portfolio/assets/page-version.js',[]);
assert.equal(current.calls.length,0);
const englishHome=run('http://example.test/sites/portfolio/en/?pv=old&project=p10#work',
  'http://example.test/sites/portfolio/assets/page-version.js',[]);
assert.equal(englishHome.calls[0].address,'/sites/portfolio/en/?project=p10#work');
const legacy=run('http://example.test/sites/portfolio/cases/p10.html?pv=old&from='+
  encodeURIComponent('/sites/portfolio/records.html?pv=old&q=库存&category=Client+work&return=p10')+'#process',
  'http://example.test/sites/portfolio/assets/page-version.js',[]);
const cleaned=new URL(legacy.calls[0].address,'http://example.test');
const origin=new URL(cleaned.searchParams.get('from'),'http://example.test');
assert.equal(origin.searchParams.has('pv'),false);
assert.equal(origin.searchParams.get('q'),'库存');
assert.equal(origin.searchParams.get('category'),'Client work');
assert.equal(origin.searchParams.get('return'),'p10');
assert.equal(cleaned.hash,'#process');
console.log('PASS: clean/legacy URLs, nested return, replace-only history, filters/hash, bilingual/subpath scope, external/media cache parameters');
