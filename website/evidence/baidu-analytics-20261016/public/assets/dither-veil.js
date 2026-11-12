/* Dither Veil by David Haz / React Bits. Native WebGL2 controller.
 * Original diffusion algorithm and all three GLSL shaders retained verbatim.
 * MIT + Commons Clause: vendor/react-bits-components/LICENSE.md.
 */
(() => {
'use strict';
const KERNELS = {
  atkinson: [
    [1, 0, 1 / 8],
    [2, 0, 1 / 8],
    [-1, 1, 1 / 8],
    [0, 1, 1 / 8],
    [1, 1, 1 / 8],
    [0, 2, 1 / 8]
  ],
  floyd: [
    [1, 0, 7 / 16],
    [-1, 1, 3 / 16],
    [0, 1, 5 / 16],
    [1, 1, 1 / 16]
  ]
};


const hexToRgb = hex => {
  let h = String(hex || '').replace('#', '');
  if (h.length === 3) h = h.replace(/./g, c => c + c);
  const n = parseInt(h.slice(0, 6), 16);
  return Number.isNaN(n) ? [0, 0, 0] : [((n >> 16) & 255) / 255, ((n >> 8) & 255) / 255, (n & 255) / 255];
};

const fitScale = (w, h, iw, ih, contain) => {
  const ratio = w / h / (iw / ih);
  if (contain) return ratio > 1 ? [ratio, 1] : [1, 1 / ratio];
  return ratio > 1 ? [1, 1 / ratio] : [ratio, 1];
};


const measureEdge = (context, image) => {
  const size = 32;
  context.canvas.width = size;
  context.canvas.height = size;
  context.drawImage(image, 0, 0, size, size);
  const data = context.getImageData(0, 0, size, size).data;
  const sum = [0, 0, 0];
  const squares = [0, 0, 0];
  let count = 0;
  for (let y = 0; y < size; y++) {
    for (let x = 0; x < size; x++) {
      if (x > 0 && y > 0 && x < size - 1 && y < size - 1) continue;
      for (let c = 0; c < 3; c++) {
        const v = data[(y * size + x) * 4 + c] / 255;
        sum[c] += v;
        squares[c] += v * v;
      }
      count++;
    }
  }
  const matte = [sum[0] / count, sum[1] / count, sum[2] / count];
  const spread =
    matte.reduce((total, mean, c) => total + Math.sqrt(Math.max(0, squares[c] / count - mean * mean)), 0) / 3;
  return { matte, plain: spread < 0.06 };
};


const diffuse = (pixels, cols, rows, kernel, levels, rgb, grade) => {
  const channels = rgb ? 3 : 1;
  const values = new Float32Array(cols * rows * channels);
  for (let i = 0; i < cols * rows; i++) {
    const r = pixels[i * 4] / 255;
    const g = pixels[i * 4 + 1] / 255;
    const b = pixels[i * 4 + 2] / 255;
    if (rgb) {
      values[i * 3] = grade(r);
      values[i * 3 + 1] = grade(g);
      values[i * 3 + 2] = grade(b);
    } else {
      values[i] = grade(0.2126 * r + 0.7152 * g + 0.0722 * b);
    }
  }
  const steps = levels - 1;
  const out = new Uint8Array(cols * rows * 4);
  for (let y = 0; y < rows; y++) {
    const dir = y & 1 ? -1 : 1;
    for (let i = 0; i < cols; i++) {
      const x = dir > 0 ? i : cols - 1 - i;
      const p = y * cols + x;
      for (let c = 0; c < channels; c++) {
        const old = values[p * channels + c];
        const q = Math.min(steps, Math.max(0, Math.round(old * steps))) / steps;
        const err = old - q;
        const byte = Math.round(q * 255);
        if (rgb) out[p * 4 + c] = byte;
        else out[p * 4] = out[p * 4 + 1] = out[p * 4 + 2] = byte;
        for (let k = 0; k < kernel.length; k++) {
          const nx = x + kernel[k][0] * dir;
          const ny = y + kernel[k][1];
          if (nx < 0 || nx >= cols || ny >= rows) continue;
          values[(ny * cols + nx) * channels + c] += err * kernel[k][2];
        }
      }
      out[p * 4 + 3] = 255;
    }
  }
  return out;
};

const vertex = `#version 300 es
in vec2 position;
in vec2 uv;
out vec2 vUv;
void main() {
  vUv = uv;
  gl_Position = vec4(position, 0.0, 1.0);
}
`;

const maskFragment = `#version 300 es
precision highp float;

uniform sampler2D tPrev;
uniform vec2 uSize;
uniform vec2 uFrom;
uniform vec2 uTo;
uniform float uRadius;
uniform float uSoftness;
uniform float uStrength;
uniform float uFade;
uniform float uHold;

in vec2 vUv;
out vec4 fragColor;

float strokeDistance(vec2 p, vec2 a, vec2 b) {
  vec2 ab = b - a;
  float h = clamp(dot(p - a, ab) / max(dot(ab, ab), 0.0001), 0.0, 1.0);
  return length(p - a - ab * h);
}

void main() {
  vec2 p = vec2(vUv.x, 1.0 - vUv.y) * uSize;
  float trail = max(texture(tPrev, vUv).r - uFade, 0.0);
  float band = max(uRadius * uSoftness, 1.0) * uHold;
  float d = strokeDistance(p, uFrom, uTo);
  trail = max(trail, clamp((uRadius - d) / band, 0.0, 1.0) * uStrength);
  fragColor = vec4(trail, 0.0, 0.0, 1.0);
}
`;

const viewFragment = `#version 300 es
precision highp float;
precision highp int;

uniform sampler2D tImage;
uniform sampler2D tMask;
uniform sampler2D tNoise;
uniform sampler2D tDiffused;
uniform vec2 uResolution;
uniform vec2 uCover;
uniform float uLod;
uniform float uCell;
uniform int uPattern;
uniform int uPalette;
uniform float uLevels;
uniform vec3 uInk;
uniform vec3 uPaper;
uniform vec3 uRimColor;
uniform float uRim;
uniform float uContrast;
uniform float uBrightness;
uniform float uReverse;
uniform float uIntro;
uniform float uHold;
uniform vec3 uMatte;
uniform float uKey;
uniform vec2 uSize;
uniform vec4 uBursts[4];
uniform float uBurstWidth;

in vec2 vUv;
out vec4 fragColor;

float bayer(vec2 cell) {
  ivec2 p = ivec2(mod(cell, 8.0));
  int v = p.x ^ p.y;
  int m = ((v & 1) << 5) | ((p.y & 1) << 4) | ((v & 2) << 2) | ((p.y & 2) << 1) | ((v & 4) >> 1) | ((p.y & 4) >> 2);
  return (float(m) + 0.5) / 64.0;
}

float blueNoise(vec2 cell) {
  return (texelFetch(tNoise, ivec2(mod(cell, 64.0)), 0).r * 255.0 + 0.5) / 256.0;
}

float engraving(vec2 cell) {
  float period = 6.0;
  float f = (mod(cell.x + cell.y, period) + 0.5) / period;
  return clamp(abs(f * 2.0 - 1.0) + (bayer(cell) - 0.5) * (2.0 / period), 0.0, 1.0);
}

vec2 imageUv(vec2 uv) {
  return (uv - 0.5) * uCover + 0.5;
}

float within(vec2 p) {
  vec2 s = step(vec2(0.0), p) * step(p, vec2(1.0));
  return s.x * s.y;
}

vec3 grade(vec3 c) {
  return pow(clamp((c - 0.5) * uContrast + 0.5 + uBrightness, 0.0, 1.0), vec3(1.6));
}

float shockwave(vec2 p) {
  float value = 0.0;
  for (int i = 0; i < 4; i++) {
    vec4 burst = uBursts[i];
    if (burst.w <= 0.0) continue;
    float offset = distance(p, burst.xy) - burst.z;
    float edge = offset > 0.0 ? offset / (uBurstWidth * 0.35) : -offset / uBurstWidth;
    value = max(value, clamp(1.0 - edge, 0.0, 1.0) * burst.w);
  }
  return value;
}

vec3 toned(vec3 c) {
  return uPalette == 1 ? grade(c) : grade(vec3(dot(c, vec3(0.2126, 0.7152, 0.0722))));
}

vec3 quantize(vec3 v, float t) {
  float steps = max(uLevels - 1.0, 1.0);
  vec3 s = v * steps;
  vec3 base = floor(s);
  return min(base + step(vec3(t), s - base), vec3(steps)) / steps;
}

void main() {
  vec2 px = vec2(gl_FragCoord.x, uResolution.y - gl_FragCoord.y);
  vec2 cell = floor(px / uCell);
  vec2 center = (cell + 0.5) * uCell;
  vec2 cellUv = vec2(center.x / uResolution.x, 1.0 - center.y / uResolution.y);

  vec2 sampleUv = imageUv(cellUv);
  float framed = within(sampleUv);
  vec3 level;
  if (uPattern == 3) {
    level = texelFetch(tDiffused, ivec2(cell), 0).rgb;
  } else {
    vec3 c = mix(uMatte, textureLod(tImage, sampleUv, uLod).rgb, framed);
    float t = uPattern == 1 ? blueNoise(cell) : (uPattern == 2 ? engraving(cell) : bayer(cell));
    level = quantize(toned(c), t);
  }

  vec3 color = mix(uInk, mix(uInk, uPaper, level), max(framed, uKey));
  vec3 backdrop = mix(uInk, uPaper, toned(uMatte));
  vec2 photoUv = imageUv(vUv);
  vec3 raw = texture(tImage, photoUv).rgb;
  float plain = uKey * (1.0 - smoothstep(0.05, 0.22, distance(raw, uMatte)));
  vec3 photo = mix(mix(uInk, backdrop, uKey), mix(raw, backdrop, plain), within(photoUv));

  vec2 point = vec2(cellUv.x, 1.0 - cellUv.y) * uSize;
  float mask = max(clamp(texture(tMask, cellUv).r * uHold, 0.0, 1.0), shockwave(point));
  float shown = mix(mask, 1.0 - mask, uReverse);
  float order = bayer(cell.yx);
  float low = order * (1.0 - uRim);
  color = mix(color, uRimColor, step(low, shown) * step(0.001, uRim));
  color = mix(color, photo, step(low + uRim, shown));

  vec2 aspect = vec2(uResolution.x / uResolution.y, 1.0);
  float spread = length((cellUv - 0.5) * aspect) / length(aspect * 0.5);
  float appear = step(spread * 0.72 + bayer(cell + vec2(3.0, 5.0)) * 0.28, uIntro * 1.001);
  fragColor = vec4(mix(uInk, color, appear), 1.0);
}
`;

const surface = document.querySelector('[data-dither-veil]');
if (!surface) return;
const canvas = surface.querySelector('canvas');
const img = surface.querySelector('img');
const button = surface.parentElement.querySelector('[data-veil-reveal]');
const reduced = matchMedia('(prefers-reduced-motion: reduce)');
const english = document.documentElement.lang === 'en';
const HOLD = 1.6, INTRO_MS = 1100, BURST_SECONDS = 1.2;
const settings = {
  levels:Number(surface.dataset.levels), brightness:Number(surface.dataset.brightness),
  ink:hexToRgb(surface.dataset.inkColor), paper:hexToRgb(surface.dataset.paperColor), rim:hexToRgb(surface.dataset.rimColor),
  pixelSize:2, contrast:1.15, revealRadius:200, softness:.6, linger:1
};
let gl, renderer, raf = 0, last = 0, introStart = 0, width = 1, height = 1;
let visible = true, leaving = false, presence = 0, trailUntil = 0, lost = false;
let imageReady = false, frames = 0, burstList = [];
const pointer = {x:0,y:0,inside:false,fresh:true};
const brush = {x:0,y:0,px:0,py:0};
const clamp = (n,a,b) => Math.max(a,Math.min(b,n));
function createRenderer() {
  gl = canvas.getContext('webgl2',{alpha:false,antialias:false,depth:false,powerPreference:'low-power'});
  if (!gl) throw new Error('WebGL2 unavailable');
  gl.disable(gl.DEPTH_TEST); gl.disable(gl.BLEND);
  let floatMask = !!gl.getExtension('EXT_color_buffer_float');
  const resources = {textures:[],buffers:[],fbos:[],programs:[],vaos:[],shaders:[]};
  const buffer = gl.createBuffer(); resources.buffers.push(buffer);
  gl.bindBuffer(gl.ARRAY_BUFFER,buffer);
  gl.bufferData(gl.ARRAY_BUFFER,new Float32Array([-1,-1,0,0,3,-1,2,0,-1,3,0,2]),gl.STATIC_DRAW);
  function shader(type,source) {
    const item=gl.createShader(type); resources.shaders.push(item);
    gl.shaderSource(item,source); gl.compileShader(item);
    if (!gl.getShaderParameter(item,gl.COMPILE_STATUS)) throw new Error(gl.getShaderInfoLog(item));
    return item;
  }
  const v=shader(gl.VERTEX_SHADER,vertex);
  function program(fragment) {
    const p=gl.createProgram(); resources.programs.push(p);
    gl.attachShader(p,v); gl.attachShader(p,shader(gl.FRAGMENT_SHADER,fragment)); gl.linkProgram(p);
    if (!gl.getProgramParameter(p,gl.LINK_STATUS)) throw new Error(gl.getProgramInfoLog(p));
    const uniforms={};
    for(let i=0;i<gl.getProgramParameter(p,gl.ACTIVE_UNIFORMS);i++) {
      const u=gl.getActiveUniform(p,i);
      uniforms[u.name.replace('[0]','')]={at:gl.getUniformLocation(p,u.name),type:u.type};
    }
    const vao=gl.createVertexArray(); resources.vaos.push(vao); gl.bindVertexArray(vao);
    gl.bindBuffer(gl.ARRAY_BUFFER,buffer);
    for(const [name,offset] of [['position',0],['uv',8]]) {
      const at=gl.getAttribLocation(p,name);
      if(at>=0){gl.enableVertexAttribArray(at);gl.vertexAttribPointer(at,2,gl.FLOAT,false,16,offset);}
    }
    return {p,vao,uniforms};
  }
  const mask=program(maskFragment), view=program(viewFragment);
  function texture() {
    const t=gl.createTexture(); resources.textures.push(t);
    gl.bindTexture(gl.TEXTURE_2D,t);
    gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_WRAP_S,gl.CLAMP_TO_EDGE);
    gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_WRAP_T,gl.CLAMP_TO_EDGE);
    gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MIN_FILTER,gl.NEAREST);
    gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MAG_FILTER,gl.NEAREST);
    gl.texImage2D(gl.TEXTURE_2D,0,gl.RGBA8,1,1,0,gl.RGBA,gl.UNSIGNED_BYTE,new Uint8Array(4));
    return t;
  }
  const photo=texture(), noise=texture(), diffused=texture();
  gl.bindTexture(gl.TEXTURE_2D,photo); gl.pixelStorei(gl.UNPACK_FLIP_Y_WEBGL,true);
  gl.texImage2D(gl.TEXTURE_2D,0,gl.RGBA,gl.RGBA,gl.UNSIGNED_BYTE,img);
  gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MIN_FILTER,gl.LINEAR_MIPMAP_LINEAR);
  gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MAG_FILTER,gl.LINEAR); gl.generateMipmap(gl.TEXTURE_2D);
  gl.pixelStorei(gl.UNPACK_FLIP_Y_WEBGL,false);
  const sampler=document.createElement('canvas');
  const context=sampler.getContext('2d',{willReadFrequently:true});
  const edge=measureEdge(context,img);
  let masks=[], dpr=1, cover=[1,1], cell=2, lastSize='';
  function deleteMasks() {
    masks.forEach(t=>{gl.deleteFramebuffer(t.fbo);gl.deleteTexture(t.texture);}); masks=[];
  }
  function makeMask(w,h) {
    const t=texture(); gl.bindTexture(gl.TEXTURE_2D,t);
    gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MIN_FILTER,gl.LINEAR);
    gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MAG_FILTER,gl.LINEAR);
    gl.texImage2D(gl.TEXTURE_2D,0,floatMask?gl.RGBA16F:gl.RGBA8,w,h,0,gl.RGBA,floatMask?gl.HALF_FLOAT:gl.UNSIGNED_BYTE,null);
    const fbo=gl.createFramebuffer(); resources.fbos.push(fbo); gl.bindFramebuffer(gl.FRAMEBUFFER,fbo);
    gl.framebufferTexture2D(gl.FRAMEBUFFER,gl.COLOR_ATTACHMENT0,gl.TEXTURE_2D,t,0);
    if(gl.checkFramebufferStatus(gl.FRAMEBUFFER)!==gl.FRAMEBUFFER_COMPLETE) throw new Error('Mask target unavailable');
    gl.clearColor(0,0,0,1);gl.clear(gl.COLOR_BUFFER_BIT);
    return {texture:t,fbo,w,h};
  }
  function draw(program,target,values,textures) {
    gl.bindFramebuffer(gl.FRAMEBUFFER,target?.fbo||null);
    gl.viewport(0,0,target?.w||canvas.width,target?.h||canvas.height);
    gl.useProgram(program.p);gl.bindVertexArray(program.vao);
    textures.forEach((t,i)=>{gl.activeTexture(gl.TEXTURE0+i);gl.bindTexture(gl.TEXTURE_2D,t);});
    for(const [key,u] of Object.entries(program.uniforms)) {
      const value=values[key];if(value===undefined) continue;
      if(u.type===gl.SAMPLER_2D||u.type===gl.INT)gl.uniform1i(u.at,value);
      else if(u.type===gl.FLOAT)gl.uniform1f(u.at,value);
      else if(u.type===gl.FLOAT_VEC2)gl.uniform2fv(u.at,value);
      else if(u.type===gl.FLOAT_VEC3)gl.uniform3fv(u.at,value);
      else if(u.type===gl.FLOAT_VEC4)gl.uniform4fv(u.at,value);
    }
    gl.drawArrays(gl.TRIANGLES,0,3);
  }
  function clear() {
    masks.forEach(t=>{gl.bindFramebuffer(gl.FRAMEBUFFER,t.fbo);gl.clearColor(0,0,0,1);gl.clear(gl.COLOR_BUFFER_BIT);});
  }
  function resize() {
    width=Math.max(1,surface.clientWidth);height=Math.max(1,surface.clientHeight);
    dpr=Math.min(devicePixelRatio||1,width<450?1:1.5);
    const key=`${width}|${height}|${dpr}`;if(key===lastSize)return;lastSize=key;
    canvas.width=Math.round(width*dpr);canvas.height=Math.round(height*dpr);
    cell=Math.max(1,Math.round(settings.pixelSize*dpr));
    cover=fitScale(canvas.width,canvas.height,img.naturalWidth,img.naturalHeight,true);
    deleteMasks();
    const mw=Math.max(2,Math.round(width*.5)),mh=Math.max(2,Math.round(height*.5));
    masks=[makeMask(mw,mh),makeMask(mw,mh)];
    const cols=Math.ceil(canvas.width/cell),rows=Math.ceil(canvas.height/cell);
    const [cx,cy]=cover,iw=img.naturalWidth,ih=img.naturalHeight;
    sampler.width=cols;sampler.height=rows;
    context.imageSmoothingEnabled=true;context.imageSmoothingQuality='high';
    context.fillStyle=`rgb(${edge.matte.map(v=>v*255).join(',')})`;context.fillRect(0,0,cols,rows);
    const sx=(.5-.5*cx)*iw,sy=(.5-.5*cy)*ih;
    const sw=cols*cell/canvas.width*cx*iw,sh=rows*cell/canvas.height*cy*ih;
    const x0=Math.max(sx,0),y0=Math.max(sy,0),x1=Math.min(sx+sw,iw),y1=Math.min(sy+sh,ih);
    if(x1>x0&&y1>y0)context.drawImage(img,x0,y0,x1-x0,y1-y0,(x0-sx)/sw*cols,(y0-sy)/sh*rows,(x1-x0)/sw*cols,(y1-y0)/sh*rows);
    const grade=v=>Math.pow(clamp((v-.5)*settings.contrast+.5+settings.brightness,0,1),1.6);
    const pixels=diffuse(context.getImageData(0,0,cols,rows).data,cols,rows,KERNELS.floyd,settings.levels,false,grade);
    gl.activeTexture(gl.TEXTURE0);gl.bindTexture(gl.TEXTURE_2D,diffused);gl.pixelStorei(gl.UNPACK_FLIP_Y_WEBGL,false);
    gl.texImage2D(gl.TEXTURE_2D,0,gl.RGBA8,cols,rows,0,gl.RGBA,gl.UNSIGNED_BYTE,pixels);
    pointer.fresh=true;clear();
  }
  function render(now,dt) {
    if(reduced.matches){presence=0;burstList=[];pointer.inside=false;clear();}
    else presence+=((pointer.inside?1:0)-presence)*(1-Math.exp(-dt/.16));
    if(pointer.fresh){brush.x=brush.px=pointer.x;brush.y=brush.py=pointer.y;pointer.fresh=false;}
    else {const k=1-Math.exp(-dt/.035);brush.x+=(pointer.x-brush.x)*k;brush.y+=(pointer.y-brush.y)*k;}
    if(presence>.002)trailUntil=now+settings.linger*1000+150;
    draw(mask,masks[1],{tPrev:0,uSize:[width,height],uFrom:[brush.px,brush.py],uTo:[brush.x,brush.y],uRadius:settings.revealRadius*(.45+.55*presence),uSoftness:settings.softness,uStrength:presence,uFade:Math.max(dt/settings.linger,floatMask?0:1.5/255),uHold:HOLD},[masks[0].texture]);
    masks.reverse();brush.px=brush.x;brush.py=brush.y;
    burstList=burstList.filter(b=>(now-b.start)/1000<BURST_SECONDS);
    const burstData=new Float32Array(16);
    burstList.forEach((b,i)=>{
      const k=Math.max(0,(now-b.start)/1000/BURST_SECONDS);
      const reach=Math.hypot(Math.max(b.x,width-b.x),Math.max(b.y,height-b.y))+Math.max(60,settings.revealRadius*.9);
      burstData.set([b.x,b.y,reach*Math.sin(k*Math.PI/2),1-k*k*k],i*4);
    });
    const intro=reduced.matches?1:Math.min(1,(now-introStart)/INTRO_MS);
    draw(view,null,{tImage:0,tMask:1,tNoise:2,tDiffused:3,uResolution:[canvas.width,canvas.height],uCover:cover,uLod:Math.log2(Math.max(cell*cover[0]*img.naturalWidth/canvas.width,1)),uCell:cell,uPattern:3,uPalette:0,uLevels:settings.levels,uInk:settings.ink,uPaper:settings.paper,uRimColor:settings.rim,uRim:0,uContrast:settings.contrast,uBrightness:settings.brightness,uReverse:0,uIntro:1-Math.pow(1-intro,2),uHold:HOLD,uMatte:edge.matte,uKey:edge.plain?1:0,uSize:[width,height],uBursts:burstData,uBurstWidth:Math.max(60,settings.revealRadius*.9)},[photo,masks[0].texture,noise,diffused]);
    return !reduced.matches&&(pointer.inside||presence>.002||burstList.length>0||now<trailUntil||intro<1);
  }
  return {resize,render,clear};
}
function stop(){cancelAnimationFrame(raf);raf=0;last=0;surface.dataset.animating='false';}
function frame(now){
  raf=0;if(!renderer||lost||leaving||document.hidden||!visible)return;
  const dt=last?clamp((now-last)/1000,.001,.05):1/60;last=now;
  const busy=renderer.render(now,dt);surface.dataset.frames=String(++frames);
  surface.dataset.animating=String(busy);
  if(busy)raf=requestAnimationFrame(frame);else last=0;
}
function wake(){if(!raf&&renderer&&!lost&&!leaving&&!document.hidden&&visible){last=performance.now();raf=requestAnimationFrame(frame);}}
function sync(){
  stop();button.hidden=!renderer||lost||reduced.matches;
  if(reduced.matches){pointer.inside=false;presence=0;burstList=[];renderer?.clear();}
  wake();
}
function boot(){
  if(!imageReady)return;
  try{renderer=createRenderer();renderer.resize();introStart=performance.now();surface.dataset.renderer='webgl2';surface.dataset.pattern='floyd';lost=false;}
  catch(error){renderer=null;surface.dataset.renderer='static-fallback';console.warn('Dither Veil static image fallback:',error.message);}
  sync();
}
function locate(event){const box=surface.getBoundingClientRect();pointer.x=event.clientX-box.left;pointer.y=event.clientY-box.top;}
function move(event){
  if(reduced.matches||!renderer||event.pointerType!=='mouse')return;
  locate(event);if(!pointer.inside){pointer.inside=true;pointer.fresh=true;}wake();
}
function leave(){pointer.inside=false;wake();}
function burst(x,y){
  if(reduced.matches||!renderer)return;
  burstList.push({x,y,start:performance.now()});if(burstList.length>4)burstList.shift();wake();
}
surface.addEventListener('pointermove',move,{passive:true});
surface.addEventListener('pointerenter',move,{passive:true});
surface.addEventListener('pointerleave',leave,{passive:true});
surface.addEventListener('pointercancel',leave,{passive:true});
surface.addEventListener('pointerdown',event=>{
  if(event.button!==0)return;locate(event);burst(pointer.x,pointer.y);
},{passive:true});
button.addEventListener('click',()=>burst(width*.5,height*.5));
button.title=english?'Reveal the image, then watch the dither return':'揭开画面后，点阵会逐渐复原';
new ResizeObserver(()=>{if(renderer&&!lost){renderer.resize();wake();}}).observe(surface);
new IntersectionObserver(([entry])=>{visible=entry.isIntersecting;if(visible)wake();else stop();}).observe(surface);
reduced.addEventListener('change',sync);
document.addEventListener('visibilitychange',sync);
window.addEventListener('pagehide',()=>{leaving=true;stop();});
window.addEventListener('pageshow',()=>{leaving=false;sync();});
canvas.addEventListener('webglcontextlost',event=>{event.preventDefault();lost=true;surface.dataset.renderer='context-lost';stop();button.hidden=true;});
canvas.addEventListener('webglcontextrestored',boot);
if(img.complete&&img.naturalWidth){imageReady=true;boot();}
else img.addEventListener('load',()=>{imageReady=true;boot();},{once:true});
img.addEventListener('error',()=>{surface.dataset.renderer='image-unavailable';button.hidden=true;},{once:true});
})();
