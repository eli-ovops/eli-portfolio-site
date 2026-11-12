'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const source=fs.readFileSync(require('node:path').join(__dirname,'../assets/depth-gallery.js'),'utf8');
const start=source.indexOf('  function render(value)');
const code=source.slice(start,source.indexOf('  function clear()',start));
const cards=Array.from({length:6},()=>({style:{},classList:{toggle(){}},setAttribute(){}}));
let poses=[];
const views=cards.map((card,i)=>({card,set(value){poses[i]=value;},setCaption(){}}));
const context={cards,views,all:cards,active:-1,stage:{dataset:{}},innerWidth:1335,
  mod:(n,size)=>((n%size)+size)%size,updateReadingMode(){},fitMobileStory(){},
  indexButtons:cards.map(()=>({setAttribute(){}})),label:{},prev:{},next:{}};
vm.runInNewContext(code,context);
context.render(0.49);
assert.ok(poses[0].opacity<=0.03,'Outgoing card must fade before its stacking order changes at the midpoint');
context.render(-0.51);
assert.ok(poses[5].opacity<=0.03,'Reverse incoming card must be nearly transparent during stacking handoff');
context.render(0);
assert.equal(poses[0].opacity,1,'Resting front card remains opaque');
assert.equal(poses[1].opacity,0.7,'Original resting rear-card appearance is preserved');
console.log('PASS: forward/reverse stack handoff is hidden by a continuous fade; resting appearance unchanged');
