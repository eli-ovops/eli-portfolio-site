/* User behavior regression: mouse reset keeps the editor focused; reset still
 * clears query/category, URL and result state, including keyboard activation. */
'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm'),path=require('node:path');
const source=fs.readFileSync(process.argv[2] || path.join(__dirname,'../app.js'),'utf8');
function fixture(english=false) {
  const listeners=new Map(), document={activeElement:null};
  function element(extra={}) {
    const handlers={};
    return Object.assign({hidden:false,value:'',dataset:{},textContent:'',
      addEventListener(type,fn){(handlers[type] ||= []).push(fn);},
      emit(type,event={}){for(const fn of handlers[type] || [])fn(event);},
      focus(){document.activeElement=this;},
      setAttribute(name,value){this[name]=value;},hasAttribute(){return false;}},extra);
  }
  const all=english?'All':'全部',client=english?'Client work':'客户参与';
  const input=element(),reset=element(),count=element(),empty=element();
  const filters=[all,client,'tools'].map(value=>element({dataset:{filter:value}}));
  const items=[element({dataset:{category:'tools',client:'true',search:'库存 inventory'}}),
    element({dataset:{category:'tools',client:'true',search:'扫码库存 inventory'}}),
    element({dataset:{category:client,client:'true',search:'RAG chatbot'}})];
  const disclosure=element({open:true,querySelectorAll(){return items;}});
  document.documentElement={lang:english?'en':'zh-CN'};
  document.querySelector=selector=>({'#search':input,'.archive-disclosure':disclosure,
    '.result-count':count,'.empty':empty,'.reset-search':reset,'[data-enhance]':element()}[selector] || null);
  document.querySelectorAll=selector=>selector==='[data-filter]'?filters:[];
  const location=new URL('http://example.test/records.html?pv=123&category='+encodeURIComponent(client)+'&q=XYZ');
  const history={replaceState(state,_,url){location.href=new URL(url,location).href;}};
  vm.runInNewContext(source,{URL,URLSearchParams,document,location,history,window:{
    addEventListener(type,fn){listeners.set(type,fn);}}});
  return {document,input,reset,count,empty,filters,items,location};
}
for(const english of [false,true]) {
  const f=fixture(english);
  f.input.focus();
  const down={button:0,defaultPrevented:false,preventDefault(){this.defaultPrevented=true;}};
  f.reset.emit('mousedown',down);
  assert.equal(down.defaultPrevented,true,'primary mouse reset must not blur active editor');
  assert.equal(f.input.value,'XYZ','mouse down alone must not clear (drag cancellation)');
  f.reset.emit('click');
  assert.equal(f.input.value,'');assert.equal(f.document.activeElement,f.input);
  assert.equal(f.items.filter(item=>!item.hidden).length,3);
  assert.equal(f.empty.hidden,true);
  assert.equal(f.location.searchParams.has('q'),false);assert.equal(f.location.searchParams.has('category'),false);
  assert.equal(f.location.searchParams.get('pv'),'123');
  // Fresh typing after reset works; keyboard click follows the ordinary reset.
  f.input.value='inventory';f.input.emit('input');
  assert.equal(f.items.filter(item=>!item.hidden).length,2);
  f.input.value='XYZ';f.input.emit('input');f.reset.focus();f.reset.emit('click');
  assert.equal(f.input.value,'');assert.equal(f.items.filter(item=>!item.hidden).length,3);
  for(const button of [1,2]) {
    const other={button,defaultPrevented:false,preventDefault(){this.defaultPrevented=true;}};
    f.reset.emit('mousedown',other);assert.equal(other.defaultPrevented,false);
  }
  f.reset.focus();const inactive={button:0,defaultPrevented:false,preventDefault(){this.defaultPrevented=true;}};
  f.reset.emit('mousedown',inactive);assert.equal(inactive.defaultPrevented,false);
}
console.log('PASS: mouse focus continuity, cancelled press, keyboard reset, fresh search, bilingual URL/result state');
