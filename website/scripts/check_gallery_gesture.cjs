'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const source = fs.readFileSync(require('node:path').join(__dirname,'../assets/depth-gallery.js'),'utf8');
const start = source.indexOf('  function gesture(delta)');
const gesture = source.slice(start,source.indexOf("  stage.addEventListener('wheel'",start));
function run(value, target, deltas, ongoing = false) {
  let scheduled, landed;
  const context = {position:{value}, target, stage:{clientHeight:600}, snapTimer:ongoing ? 1 : 0,
    gestureOrigin:ongoing ? Math.floor(value) : null, gestureDistance:0, smoothing(){},
    clearTimeout(){},setTimeout(callback){scheduled=callback;return 1;},go(n){landed=n;}};
  vm.runInNewContext(gesture,context);
  deltas.forEach(delta=>context.gesture(delta)); scheduled();
  return landed;
}
assert.equal(run(0.68,0.72,[-0.2]),1,'A tiny reverse tail must not snap an already advanced card backwards');
assert.equal(run(0,0,[120]),1,'A deliberate mouse-wheel notch still advances one card');
assert.equal(run(0,0,[120,-0.2]),1,'A small reverse tail must not cancel deliberate forward input');
assert.equal(run(0,0,[-120]),-1,'Reverse mouse-wheel notch still selects the preceding card');
assert.equal(run(0,0,[5,-2]),0,'Tiny trackpad jitter stays on the nearest card');
assert.equal(run(0.7,0.7,[240],true),1,'An ongoing gesture already near the next card must not skip an extra card');
console.log('PASS: nearest-card settling, stable gesture direction, mouse-wheel notches and trackpad jitter');
