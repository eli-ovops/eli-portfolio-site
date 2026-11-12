'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const source=fs.readFileSync(require('node:path').join(__dirname,'../assets/depth-gallery.js'),'utf8');
const start=source.indexOf('  function createFollower()');
const code=source.slice(start,source.indexOf('  function clear()',start));
function create() {
  let tick=null,adds=0;
  const context={position:{value:0},target:0,render(){},gsap:{ticker:{
    add(fn){tick=fn;adds++;},remove(fn){if(tick===fn)tick=null;}}}};
  vm.runInNewContext(code,context);
  return {context,follow:context.createFollower(),step(){tick?.(0,1000/60);},
    get active(){return !!tick;},get adds(){return adds;},get value(){return context.position.value;}};
}
const a=create();a.follow(1);let prev=0;
for(let i=0;i<120;i++){a.step();assert.ok(a.value>=prev&&a.value<=1,'No overshoot while settling forward');prev=a.value;}
assert.equal(a.value,1);assert.equal(a.active,false,'Ticker stops when settled');
const b=create(),c=create();b.follow(1);c.follow(1);
for(let i=0;i<4;i++){b.step();c.step();}
c.follow(1);b.step();c.step();
assert.equal(c.value,b.value,'Repeated wheel targets do not restart or slow the motion');
assert.equal(c.adds,1,'Only one animation callback owns an ongoing gesture');
const before=c.value;c.follow(-1);
assert.equal(c.value,before,'Retargeting must not jump position');
for(let i=0;i<120;i++)c.step();
assert.equal(c.value,-1,'Reverse target settles exactly');assert.equal(c.active,false);
b.follow(3);b.follow(2);b.follow(4);
assert.equal(b.adds,1,'Rapid retargets reuse the same ticker');b.follow.stop();
assert.equal(b.active,false,'Teardown removes the animation callback');
console.log('PASS: continuous retargeting, forward/reverse settling without overshoot and ticker cleanup');
