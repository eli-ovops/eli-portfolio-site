'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm'),path=require('node:path');
const source=fs.readFileSync(path.join(__dirname,'../assets/site-analytics.js'),'utf8');
function boot({url='https://www.eliai.cn/services/ai-agent.html?pv=release&q=private&from=secret#cases',choice=null,blocked=false,canonical='https://www.eliai.cn/services/ai-agent.html'}={}) {
 const location=new URL(url);let reloads=0;location.reload=()=>{reloads++;};
 const notice={hidden:true},dialog={open:false,showModal(){this.open=true;},close(){this.open=false;}};
 const scripts=[],buttons=[{hidden:true}],events={},store={};if(choice)store['eli-analytics-consent-20261016']=choice;
 const context={URL,location,window:{},document:{currentScript:{dataset:{baiduSite:'1234567890abcdef1234567890abcdef',consentVersion:'20261016'}},documentElement:{dataset:{}},
  querySelector(){return canonical?{href:canonical}:null;},getElementById(id){return id==='analytics-notice'?notice:dialog;},querySelectorAll(){return buttons;},
  createElement(){return {};},head:{appendChild(s){scripts.push(s);}},addEventListener(name,fn){events[name]=fn;}},
 localStorage:{getItem(k){if(blocked)throw Error('blocked');return store[k]||null;},setItem(k,v){if(blocked)throw Error('blocked');store[k]=v;}},
 addEventListener(name,fn){events[name]=fn;}};
 vm.runInNewContext(source,context);
 const click=(linkOrChoice,selectors=[])=>events.click?.({target:{closest(selector){
  if(selector==='[data-analytics-choice]'&&['allow','deny'].includes(linkOrChoice))return {dataset:{analyticsChoice:linkOrChoice}};
  if(selector==='a[href]'&&linkOrChoice.startsWith('http')||selector==='a[href]'&&/^(mailto:|tel:)/.test(linkOrChoice))return {href:linkOrChoice,closest(s){return selectors.includes(s)?{}:null;}};
  return null;
 }}});
 return {context,notice,dialog,scripts,events,store,click,reloads:()=>reloads,queue:()=>JSON.parse(JSON.stringify(context.window._hmt||[])),repeat(){vm.runInNewContext(source,context);}};
}
for(const url of ['http://127.0.0.1:4178/index.html','http://[REDACTED_HOST]/sites/portfolio/','https://eliai.cn/','https://preview.eliai.cn/']) {
 const x=boot({url,choice:'allow'});assert.equal(x.scripts.length,0);assert.equal(Object.keys(x.events).length,0);
}
assert.equal(boot({canonical:null,choice:'allow'}).scripts.length,0);
let x=boot();assert.equal(x.scripts.length,0);assert.equal(x.notice.hidden,false);
x.click('https://www.eliai.cn/about.html#contact',['.service-actions']);assert.equal(x.queue().length,0);
x.click('allow');assert.equal(x.scripts.length,1);assert.equal(x.scripts[0].async,true);assert.match(x.scripts[0].src,/^https:\/\/hm\.baidu\.com\/hm\.js\?[a-f0-9]{32}$/);
assert.deepEqual(x.queue(),[['_setAutoPageview',false],['_trackPageview','/services/ai-agent.html']]);
x.click('https://www.eliai.cn/about.html?pv=latest#contact',['.service-actions']);
assert.deepEqual(x.queue().at(-1),['_trackEvent','consultation','entry_click','/services/ai-agent.html|service_top']);
for(const [href,action] of [['mailto:[REDACTED_EMAIL]','email_click'],['tel:+1234567','phone_click'],['https://wa.me/1234567','whatsapp_click'],['https://www.eliai.cn/assets/wechat-qr.png','wechat_qr_click']]) {
 x.click(href,['#contact']);assert.equal(x.queue().at(-1)[2],action);assert.equal(x.queue().at(-1)[3],'/services/ai-agent.html|contact_details');
}
const count=x.queue().length;x.click('https://external.test/about.html#contact');x.click('https://www.eliai.cn/cases/p10.html');assert.equal(x.queue().length,count);
assert.doesNotMatch(JSON.stringify(x.queue()),/private|example\.test|1234567|q=|from=|pv=/);
x.events.pageshow({persisted:false});assert.equal(x.queue().length,count);
x.events.pageshow({persisted:true});assert.equal(x.queue().length,count+1);
x.repeat();assert.equal(x.scripts.length,1);
x.click('deny');assert.equal(x.reloads(),1);const after=x.queue().length;x.click('mailto:[REDACTED_EMAIL]');assert.equal(x.queue().length,after);
x=boot({choice:'deny'});assert.equal(x.scripts.length,0);assert.equal(x.notice.hidden,true);
x=boot({blocked:true});x.click('allow');assert.equal(x.scripts.length,1);x.click('deny');assert.equal(x.reloads(),1);
x=boot({choice:'allow'});x.events.storage({key:'eli-analytics-consent-20261016',newValue:'deny'});assert.equal(x.reloads(),1);
console.log('PASS: consent gating, production-only, canonical PV, precise consultation/channel clicks, no query/contact payloads, BFCache, duplicate load, blocked storage and cross-tab withdrawal');
