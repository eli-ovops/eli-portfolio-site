/* Regression: versioning preserves history/query/hash and stays inside this site. */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const source = fs.readFileSync(path.join(__dirname,'../assets/page-version.js'),'utf8');
const revision = '1234567890abcdef1234';
function run(url, script, hrefs) {
  const location = new URL(url), state = {eliAboutQuestions:[1],portfolioGallery:{index:2}};
  const calls=[], events={}, links=hrefs.map(href=>({href:new URL(href,url).href}));
  const context={URL,location,history:{state,replaceState:(saved,_,address)=>calls.push({saved,address})},
    document:{currentScript:{src:script},querySelector:()=>({content:revision}),querySelectorAll:()=>links,
      addEventListener:(event,fn)=>{events[event]=fn;}},addEventListener:(event,fn)=>{events[event]=fn;}};
  vm.runInNewContext(source,context);
  return {calls,links,state,events};
}
const result=run('http://example.test/sites/portfolio/records.html?category=Client%20work&q=inventory&return=p10#project-p10',
  'http://example.test/sites/portfolio/assets/page-version.js?v=asset',
  ['cases/p10.html','en/records.html','#main','/login','https://social.test/profile','assets/image.png']);
assert.equal(result.calls.length,1);
assert.equal(result.calls[0].saved,result.state);
const address=new URL(result.calls[0].address,'http://example.test');
assert.equal(address.searchParams.get('q'),'inventory');
assert.equal(address.searchParams.get('category'),'Client work');
assert.equal(address.searchParams.get('return'),'p10');
assert.equal(address.hash,'#project-p10');
assert.equal(address.searchParams.get('pv'),revision);
for (const link of result.links.slice(0,3)) assert.equal(new URL(link.href,'http://example.test').searchParams.get('pv'),revision);
assert.equal(result.links[3].href,'http://example.test/login');
assert.equal(result.links[4].href,'https://social.test/profile');
assert.equal(result.links[5].href,'http://example.test/sites/portfolio/assets/image.png');
const english=run('http://example.test/sites/portfolio/en/cases/p10.html',
  'http://example.test/sites/portfolio/assets/page-version.js',['../../records.html']);
assert.ok(english.calls[0].address.startsWith('/sites/portfolio/en/cases/p10.html?pv='));
assert.equal(new URL(english.links[0].href,'http://example.test').pathname,'/sites/portfolio/records.html');
const current=run('http://example.test/sites/portfolio/?pv='+revision,
  'http://example.test/sites/portfolio/assets/page-version.js',[]);
assert.equal(current.calls.length,0);
console.log('PASS: replace-only navigation, reading state, filters/hash, bilingual/subpath scope, external/media links and current version');
