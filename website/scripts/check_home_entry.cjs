'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const html = fs.readFileSync(path.join(__dirname,'..','dist','index.html'),'utf8');
const inline = html.match(/<script>\s*([\s\S]*?)<\/script>/)[1];
assert.ok(html.indexOf(inline) < html.indexOf('defer'), 'input guard must install before deferred animations');
function run(from, type, to) {
  const callbacks = {};
  let skipped = 0;
  const location = new URL(from,'http://127.0.0.1:4178');
  vm.runInNewContext(inline,{location,URL,addEventListener:(name, callback)=>callbacks[name]=callback});
  callbacks[type]({viewTransition:{skipTransition:()=>skipped++},activation:{entry:{url:new URL(to||from,location).href}}});
  return skipped;
}
for (const prefix of ['/','/en/','/sites/portfolio/','/sites/portfolio/en/']) {
  assert.equal(run(prefix+'index.html','pagereveal'),1);
  assert.equal(run(prefix,'pagereveal'),1);
  assert.equal(run(prefix+'about.html','pageswap',prefix+'index.html'),1);
  assert.equal(run(prefix+'cases/p36.html','pageswap',prefix+'cases/p05.html'),1);
  assert.equal(run(prefix+'records.html','pageswap',prefix+'cases/p10.html'),0);
  assert.equal(run(prefix+'cases/p10.html','pageswap',prefix+'records.html'),0);
  assert.equal(run(prefix+'about.html','pageswap','https://example.com/'),0);
}
const css=fs.readFileSync(path.join(__dirname,'..','assets','bits-ui.css'),'utf8');
assert.match(css,/:root\s*\{\s*view-transition-name:none;/);
assert.match(css,/::view-transition-new\(\*\)\s*\{\s*pointer-events:none;/);
console.log('PASS: early home/unrelated-route snapshot cancellation; shared title routes retained; snapshots cannot take input');
