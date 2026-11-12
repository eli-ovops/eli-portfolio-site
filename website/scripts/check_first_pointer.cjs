'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const source = fs.readFileSync(path.join(__dirname, '..', 'motion.js'), 'utf8');
function skips(from, to, options = {}, controller = source) {
  let handler, skipped = 0;
  const current = new URL(from, 'http://127.0.0.1:4178');
  vm.runInNewContext(controller, {
    URL, location: current, window: {},
    document: {documentElement: {}}, matchMedia: () => ({matches: false}),
    addEventListener: (name, callback) => { if (name === 'pageswap') handler = callback; }
  });
  assert.equal(typeof handler, 'function');
  handler({activation: options.noActivation ? undefined : {entry: {url: new URL(to, current).href}, navigationType: options.navigationType || 'push'},
    viewTransition: options.noTransition ? undefined : {skipTransition: () => skipped++}});
  return skipped;
}
for (const prefix of ['/', '/en/', '/sites/portfolio/', '/sites/portfolio/en/']) {
  assert.equal(skips(prefix+'index.html', prefix+'records.html?pv=123'), 1);
  assert.equal(skips(prefix+'about.html', prefix+'records.html'), 1);
  assert.equal(skips(prefix+'records.html', prefix+'about.html'), 1);
  assert.equal(skips(prefix+'index.html', prefix+'cases/p10.html'), 1);
  assert.equal(skips(prefix+'cases/p09.html', prefix+'cases/p10.html'), 1);
  assert.equal(skips(prefix+'records.html', prefix+'cases/p10.html'), 0);
  assert.equal(skips(prefix+'cases/p10.html', prefix+'records.html?return=p10&q=stock'), 0);
  assert.equal(skips(prefix+'about.html', prefix+'index.html'), 0);
}
assert.equal(skips('/index.html', 'https://example.com/records.html'), 0);
assert.equal(skips('/index.html', '/records.html', {noActivation: true}), 0);
assert.equal(skips('/index.html', '/records.html', {noTransition: true}), 0);
// The head controller runs before deferred motion: cancelling on arrival or on
// pointerdown is too late when the browser retains an outgoing history snapshot.
const layout = fs.readFileSync(process.argv[2] || path.join(__dirname,'../templates/layout.html'),'utf8');
const head = [...layout.matchAll(/<script>([\s\S]*?)<\/script>/g)]
  .map(match=>match[1]).find(script=>script.includes("addEventListener('pageswap'"));
assert.ok(head, 'early navigation controller must exist');
for (const prefix of ['/', '/en/', '/sites/portfolio/', '/sites/portfolio/en/']) {
  const detail=prefix+'cases/p10.html', list=prefix+'records.html?q=inventory';
  assert.equal(skips(detail,list,{navigationType:'traverse'},head),1,'Back must release the list before its first mouse press');
  assert.equal(skips(detail,list,{navigationType:'push'},head),0,'explicit return retains the shared title');
  assert.equal(skips(prefix+'records.html',detail,{navigationType:'push'},head),0,'case entry retains the shared title');
  assert.equal(skips(prefix+'about.html',list,{},head),1,'unrelated navigation remains cancelled');
}
assert.equal(skips('/cases/p10.html','https://example.com/records.html',{navigationType:'traverse'},head),0);
assert.equal(skips('/cases/p10.html','/records.html',{noTransition:true},head),0);
assert.equal(skips('/cases/p10.html','/records.html',{noActivation:true},head),0);
console.log('PASS: history list first-pointer release, shared title on explicit navigation, prefixes and fallback');
