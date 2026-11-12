'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const source = fs.readFileSync(path.join(__dirname, '..', 'motion.js'), 'utf8');
function skips(from, to, options = {}) {
  let handler, skipped = 0;
  const current = new URL(from, 'http://127.0.0.1:4178');
  vm.runInNewContext(source, {
    URL, location: current, window: {},
    document: {documentElement: {}}, matchMedia: () => ({matches: false}),
    addEventListener: (name, callback) => { if (name === 'pageswap') handler = callback; }
  });
  assert.equal(typeof handler, 'function');
  handler({activation: options.noActivation ? undefined : {entry: {url: new URL(to, current).href}},
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
console.log('PASS: early editorial transition cancellation; shared title, home curtain and fallback preserved');
