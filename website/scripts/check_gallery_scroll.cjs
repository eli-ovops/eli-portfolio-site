'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const source = fs.readFileSync(path.join(__dirname, '../assets/depth-gallery.js'), 'utf8');
// Execute the actual controller's gesture policy and wheel handler without animation timing.
const helperStart = source.search(/  function (?:captionCanScroll|isImageGesture)\(/);
const helper = source.slice(helperStart, source.indexOf('  function leaveScene', helperStart));
const wheelStart = source.indexOf("  stage.addEventListener('wheel'");
const wheel = source.slice(wheelStart, source.indexOf("  stage.addEventListener('touchstart'", wheelStart));
class Element {
  constructor(image = null, caption = null) { this.image = image; this.caption = caption; }
  closest(selector) { return selector === '.project-image' ? this.image : this.caption; }
}
const image = new Element(); image.image = image;
const caption = new Element(); caption.caption = caption;
caption.clientHeight = caption.scrollHeight = 500;
const controls = new Element();
const imageChild = new Element(image);
let open = false, handler, moves = [];
const mobile = {matches:false};
const stage = {clientHeight:600, addEventListener(name, callback) { handler = callback; }};
const nextImage = new Element(); nextImage.image = nextImage;
const cards = [{querySelector(){ return image; }}, {querySelector(){return nextImage;}}];
const context = {Element, stage, mobile, smoothing:{}, cards, all:cards, active:0,
  storyOpen:()=>open, gesture:delta=>moves.push(delta)};
vm.runInNewContext(helper + wheel, context);
function dispatch(target, extras = {}) {
  moves = []; let prevented = 0;
  handler({target,deltaY:70,deltaX:0,deltaMode:0,ctrlKey:false,
    preventDefault(){prevented++;},...extras});
  return {prevented, moves:[...moves]};
}
assert.equal(dispatch(caption).prevented,0,'Reading text must scroll the page instead of switching projects');
assert.equal(dispatch(controls).prevented,0,'Navigation controls must not capture page scrolling');
assert.deepEqual(dispatch(imageChild),{prevented:1,moves:[70]},'Collapsed current image retains switching');
open = true;
assert.equal(dispatch(image).prevented,0,'Expanded reading must not capture wheel, even over its image');
open = false; mobile.matches = true;
assert.equal(dispatch(image).prevented,0,'Mobile keeps natural page scrolling');
mobile.matches = false;
assert.equal(dispatch(image,{ctrlKey:true}).prevented,0,'Zoom gestures remain native');
assert.equal(dispatch(new Element(new Element())).prevented,0,'Images outside this gallery must not capture switching');
context.active = 1;
assert.equal(dispatch(imageChild).prevented,1,'An ongoing wheel transaction on the outgoing image must remain smooth after selection changes');
context.active = 0;
assert.deepEqual(dispatch(image,{deltaY:2,deltaMode:1}).moves,[32],'Line-mode wheels remain normalized');
assert.deepEqual(dispatch(image,{deltaY:1,deltaMode:2}).moves,[600],'Page-mode wheels remain normalized');
console.log('PASS: text/controls/expanded reading/mobile/zoom scroll natively; current image switching preserved');
