/* Adapted from React Bits Pattern Waves by David Haz (2026).
 * https://github.com/DavidHDev/react-bits/tree/main/src/content/Backgrounds/PatternWaves
 * MIT + Commons Clause; see assets/vendor/react-bits-pattern-waves/LICENSE.md.
 * Original GLSL preserved; native WebGL2 lifecycle replaces React/OGL wrappers.
 */
(() => {
'use strict';
const passVertex = `#version 300 es
in vec2 position;
void main() {
  gl_Position = vec4(position, 0.0, 1.0);
}
`;

const fieldFragment = `#version 300 es
precision highp float;
precision highp int;
uniform vec2 uSize;
uniform float uDpr;
uniform vec2 uOrigin;
uniform vec2 uPitch;
uniform int uWave;
uniform float uTime;
uniform float uUnit;
uniform vec2 uHeading;
uniform float uAmp;
uniform float uDepth;
uniform vec3 uLight;
uniform float uShine;
uniform float uContrast;
uniform float uInk;
uniform float uOpacity;
uniform int uFade;
uniform float uFadeSize;
uniform float uAppear;
uniform sampler2D tRipple;
uniform float uRipple;
out vec4 fragColor;

const float FOLDS = 5.5;

uvec3 scramble(uvec3 v) {
  v = v * 1664525u + 1013904223u;
  v.x += v.y * v.z;
  v.y += v.z * v.x;
  v.z += v.x * v.y;
  v ^= v >> 16u;
  v.x += v.y * v.z;
  v.y += v.z * v.x;
  v.z += v.x * v.y;
  return v;
}

vec3 lattice(vec3 corner) {
  uvec3 h = scramble(uvec3(ivec3(corner) + 4096));
  return vec3(h & 65535u) / 32767.5 - 1.0;
}

float gradientNoise(vec3 p) {
  vec3 i = floor(p);
  vec3 f = p - i;
  vec3 u = f * f * f * (f * (f * 6.0 - 15.0) + 10.0);
  float n000 = dot(lattice(i), f);
  float n100 = dot(lattice(i + vec3(1.0, 0.0, 0.0)), f - vec3(1.0, 0.0, 0.0));
  float n010 = dot(lattice(i + vec3(0.0, 1.0, 0.0)), f - vec3(0.0, 1.0, 0.0));
  float n110 = dot(lattice(i + vec3(1.0, 1.0, 0.0)), f - vec3(1.0, 1.0, 0.0));
  float n001 = dot(lattice(i + vec3(0.0, 0.0, 1.0)), f - vec3(0.0, 0.0, 1.0));
  float n101 = dot(lattice(i + vec3(1.0, 0.0, 1.0)), f - vec3(1.0, 0.0, 1.0));
  float n011 = dot(lattice(i + vec3(0.0, 1.0, 1.0)), f - vec3(0.0, 1.0, 1.0));
  float n111 = dot(lattice(i + vec3(1.0, 1.0, 1.0)), f - vec3(1.0, 1.0, 1.0));
  return mix(
    mix(mix(n000, n100, u.x), mix(n010, n110, u.x), u.y),
    mix(mix(n001, n101, u.x), mix(n011, n111, u.x), u.y),
    u.z
  );
}

vec2 turn(vec2 v, float angle) {
  float c = cos(angle);
  float s = sin(angle);
  return vec2(c * v.x - s * v.y, s * v.x + c * v.y);
}

float surface(vec2 p, float t) {
  if (uWave == 0) {
    vec2 side = vec2(-uHeading.y, uHeading.x);
    float u = dot(p, uHeading);
    float v = dot(p, side);
    float bend = gradientNoise(vec3(v * 0.85, u * 0.3, t * 0.05)) * 1.7 + 0.4 * sin(v * 1.6 + t * 0.2);
    float phase = u * FOLDS + bend - t * 0.45;
    float swell = 0.6 + 0.4 * gradientNoise(vec3(u * 0.55 + 3.0, v * 0.45, t * 0.04));
    float fold = sin(phase) + 0.32 * sin(2.0 * phase + 1.3);
    float ripple = 0.16 * sin(u * FOLDS * 2.5 + bend * 1.9 - t * 0.9 + 2.1);
    return (fold + ripple) * swell;
  }
  if (uWave == 1) {
    float bend = gradientNoise(vec3(p * 0.6, t * 0.05)) * 0.6;
    float phase = dot(p, uHeading) * 15.0 + bend * 2.2 - t * 1.4;
    float swell = sin(phase) + 0.3 * sin(2.0 * phase - 0.8);
    float roll = 0.75 + 0.25 * gradientNoise(vec3(p * 0.9 + 11.0, t * 0.05));
    return 0.8 * swell * roll;
  }
  float r = length(p + uHeading * 1.2);
  float bend = gradientNoise(vec3(p * 1.2, t * 0.05)) * 0.1;
  return sin((r + bend) * 9.0 - t * 1.8) * (0.45 + 0.55 * exp(-(r - 0.6) * 0.8));
}

float heightAt(vec2 css) {
  float h = surface((css - 0.5 * uSize) / uUnit, uTime) * uAmp;
  if (uRipple > 0.0) h += texture(tRipple, css / uSize).r * uRipple;
  return h;
}

void main() {
  vec2 cell = floor(gl_FragCoord.xy);
  vec2 center = uOrigin + (cell + 0.5) * uPitch;
  vec2 css = center / uDpr;
  vec2 uv = css / uSize;
  float e = max(uPitch.y / uDpr, 4.0);
  float h = heightAt(css);
  float hx = (heightAt(css + vec2(e, 0.0)) - heightAt(css - vec2(e, 0.0))) / (2.0 * e);
  float hy = (heightAt(css + vec2(0.0, e)) - heightAt(css - vec2(0.0, e))) / (2.0 * e);
  vec2 grad = vec2(hx, hy) * uUnit * uDepth * 0.4;
  vec3 n = normalize(vec3(-grad, 1.0));

  float diffuse = clamp(dot(n, uLight), 0.0, 1.0);
  vec3 halfway = normalize(uLight + vec3(0.0, 0.0, 1.0));
  float spec = pow(clamp(dot(n, halfway), 0.0, 1.0), 160.0) * uShine * 1.15;
  float hollow = 0.7 + 0.3 * clamp(h * 0.5 + 0.5, 0.0, 1.0);
  float tone = clamp(diffuse * hollow * 0.78 + spec, 0.0, 1.0);
  tone = clamp((tone - 0.42) * uContrast + 0.42, 0.0, 1.0);

  float level = uInk > 0.5 ? pow(clamp(1.0 - tone / 0.46, 0.0, 1.0), 2.4) * 0.72 : pow(tone, 2.2);
  float emphasis = uInk > 0.5 ? smoothstep(0.55, 0.95, level) : clamp(spec * 1.6, 0.0, 1.0);

  float fade = 1.0;
  vec2 c = uv * 2.0 - 1.0;
  if (uFade == 1) {
    fade = 1.0 - smoothstep(1.0 - uFadeSize, 1.18, length(c));
  } else if (uFade == 2) {
    fade = mix(0.05, 1.0, smoothstep(0.08, 0.08 + uFadeSize, length(c * vec2(1.0, 1.35))));
  } else if (uFade == 3) {
    fade = smoothstep(0.0, uFadeSize, uv.y);
  } else if (uFade == 4) {
    fade = smoothstep(0.0, uFadeSize, 1.0 - uv.y);
  }

  float reach = length(css - 0.5 * uSize) / max(0.5 * length(uSize), 1.0);
  float appear = smoothstep(reach - 0.05, reach + 0.3, uAppear * 1.35);

  float alpha = uOpacity * fade * appear * (0.22 + 0.78 * level);
  float lift = clamp(h * uDepth * 0.42, -0.48, 0.48);
  fragColor = vec4(level, alpha, emphasis, lift + 0.5);
}
`;

const rippleFragment = `#version 300 es
precision highp float;
uniform sampler2D tState;
uniform vec2 uTexel;
uniform vec2 uSize;
uniform vec2 uFrom;
uniform vec2 uTo;
uniform float uRadius;
uniform float uImpulse;
uniform float uDamping;
out vec4 fragColor;

void main() {
  vec2 uv = gl_FragCoord.xy * uTexel;
  vec2 state = texture(tState, uv).rg;
  float left = texture(tState, uv - vec2(uTexel.x, 0.0)).r;
  float right = texture(tState, uv + vec2(uTexel.x, 0.0)).r;
  float below = texture(tState, uv - vec2(0.0, uTexel.y)).r;
  float above = texture(tState, uv + vec2(0.0, uTexel.y)).r;
  float next = ((left + right + below + above) * 0.5 - state.g) * uDamping;
  vec2 p = uv * uSize;
  vec2 segment = uTo - uFrom;
  float along = clamp(dot(p - uFrom, segment) / max(dot(segment, segment), 1e-4), 0.0, 1.0);
  float d = length(p - uFrom - segment * along) / uRadius;
  next -= uImpulse * exp(-d * d * 2.0);
  fragColor = vec4(next, state.r, 0.0, 1.0);
}
`;

const markFragment = `#version 300 es
precision highp float;
precision highp int;
uniform sampler2D tField;
uniform sampler2D tAtlas;
uniform vec2 uOrigin;
uniform vec2 uPitch;
uniform vec2 uGrid;
uniform int uPattern;
uniform float uMarkSize;
uniform float uStroke;
uniform vec3 uColor;
uniform vec3 uAccent;
uniform vec4 uBackground;
uniform vec3 uAtlas;
out vec4 fragColor;

float box(vec2 p, vec2 b, float r) {
  vec2 q = abs(p) - b + r;
  return length(max(q, 0.0)) + min(max(q.x, q.y), 0.0) - r;
}

float coverage(vec2 local, float level) {
  float span = uPitch.y * uMarkSize;
  float area = max(sqrt(level), 0.14);
  if (uPattern == 0) {
    return clamp(0.5 - (length(local) - 0.5 * span * area), 0.0, 1.0);
  }
  if (uPattern == 1) {
    float extent = 0.5 * span * area;
    return clamp(0.5 - box(local, vec2(extent), extent * 0.3), 0.0, 1.0);
  }
  if (uPattern == 2) {
    float arm = 0.5 * span * mix(0.3, 1.0, level);
    float width = 0.5 * uStroke;
    return clamp(0.5 - min(box(local, vec2(arm, width), width), box(local, vec2(width, arm), width)), 0.0, 1.0);
  }
  if (uAtlas.z < 1.0) return 0.0;
  vec2 g = local / span + 0.5;
  if (g.x < 0.0 || g.y < 0.0 || g.x > 1.0 || g.y > 1.0) return 0.0;
  float index = min(floor(level * uAtlas.z), uAtlas.z - 1.0);
  vec2 tile = vec2(mod(index, uAtlas.x), floor(index / uAtlas.x));
  vec2 atlasUv = (tile + vec2(g.x, 1.0 - g.y)) / uAtlas.xy;
  vec2 texel = 1.0 / (span * uAtlas.xy);
  return textureGrad(tAtlas, atlasUv, vec2(texel.x, 0.0), vec2(0.0, texel.y)).a;
}

vec4 lineInk(vec2 rel) {
  float fx = rel.x / uPitch.x - 0.5;
  float c0 = clamp(floor(fx), 0.0, uGrid.x - 1.0);
  float c1 = min(c0 + 1.0, uGrid.x - 1.0);
  float t = clamp(fx - c0, 0.0, 1.0);
  float row = floor(rel.y / uPitch.y);
  vec4 ink = vec4(0.0);
  for (int k = -1; k <= 1; k++) {
    float cy = row + float(k);
    if (cy < 0.0 || cy >= uGrid.y) continue;
    vec4 a = texelFetch(tField, ivec2(int(c0), int(cy)), 0);
    vec4 b = texelFetch(tField, ivec2(int(c1), int(cy)), 0);
    vec4 f = mix(a, b, t);
    if (f.g < 0.002) continue;
    float y = (cy + 0.5 + f.a - 0.5) * uPitch.y;
    float slope = (b.a - a.a) * uPitch.y / uPitch.x;
    float thickness = max(uStroke, uPitch.y * uMarkSize * f.r);
    float d = abs(rel.y - y) / sqrt(1.0 + slope * slope) - 0.5 * thickness;
    float alpha = clamp(0.5 - d, 0.0, 1.0) * f.g;
    if (alpha > ink.a) ink = vec4(mix(uColor, uAccent, f.b) * alpha, alpha);
  }
  return ink;
}

void main() {
  vec2 rel = gl_FragCoord.xy - uOrigin;
  vec4 background = vec4(uBackground.rgb * uBackground.a, uBackground.a);
  vec4 ink = vec4(0.0);
  if (uPattern == 3) {
    ink = lineInk(rel);
  } else {
    float cx = floor(rel.x / uPitch.x);
    float row = floor(rel.y / uPitch.y);
    if (cx >= 0.0 && cx < uGrid.x) {
      for (int k = -1; k <= 1; k++) {
        float cy = row + float(k);
        if (cy < 0.0 || cy >= uGrid.y) continue;
        vec4 f = texelFetch(tField, ivec2(int(cx), int(cy)), 0);
        if (f.g < 0.002) continue;
        vec2 center = (vec2(cx, cy) + 0.5) * uPitch + vec2(0.0, (f.a - 0.5) * uPitch.y);
        float alpha = coverage(rel - center, f.r) * f.g;
        if (alpha > ink.a) ink = vec4(mix(uColor, uAccent, f.b) * alpha, alpha);
      }
    }
  }
  fragColor = ink + background * (1.0 - ink.a);
}
`;

const layer=document.querySelector('[data-home-ambient]');
const control=document.querySelector('[data-ambient-control]');
if (!layer || !control) return;
const canvas=layer.querySelector('canvas');
const reduce=matchMedia('(prefers-reduced-motion: reduce)');
const fine=matchMedia('(hover: hover) and (pointer: fine)');
const english=document.documentElement.lang==='en';
const clamp=(n,a,b)=>Math.min(b,Math.max(a,n));
let userPaused=false, leaving=false, frameId=0, last=0, time=0, engine, lost=false;
try { userPaused=sessionStorage.getItem('eli-home-ambient-paused')==='true'; } catch (_) {}

function createEngine() {
  const gl=canvas.getContext('webgl2',{alpha:true,premultipliedAlpha:true,antialias:false,depth:false,powerPreference:'low-power'});
  if (!gl) throw new Error('WebGL2 unavailable');
  gl.disable(gl.DEPTH_TEST);gl.disable(gl.BLEND);gl.clearColor(0,0,0,0);
  const buffer=gl.createBuffer();gl.bindBuffer(gl.ARRAY_BUFFER,buffer);
  gl.bufferData(gl.ARRAY_BUFFER,new Float32Array([-1,-1,3,-1,-1,3]),gl.STATIC_DRAW);
  const shaderObjects=[];
  function shader(type,source) {
    const s=gl.createShader(type);gl.shaderSource(s,source);gl.compileShader(s);shaderObjects.push(s);
    if (!gl.getShaderParameter(s,gl.COMPILE_STATUS)) throw new Error(gl.getShaderInfoLog(s));
    return s;
  }
  const vertex=shader(gl.VERTEX_SHADER,passVertex);
  function program(fragment) {
    const p=gl.createProgram();gl.attachShader(p,vertex);gl.attachShader(p,shader(gl.FRAGMENT_SHADER,fragment));gl.linkProgram(p);
    if (!gl.getProgramParameter(p,gl.LINK_STATUS)) throw new Error(gl.getProgramInfoLog(p));
    const uniforms={};
    for (let i=0;i<gl.getProgramParameter(p,gl.ACTIVE_UNIFORMS);i++) {
      const u=gl.getActiveUniform(p,i);uniforms[u.name]={location:gl.getUniformLocation(p,u.name),type:u.type};
    }
    const vao=gl.createVertexArray();gl.bindVertexArray(vao);gl.bindBuffer(gl.ARRAY_BUFFER,buffer);
    const a=gl.getAttribLocation(p,'position');gl.enableVertexAttribArray(a);gl.vertexAttribPointer(a,2,gl.FLOAT,false,0,0);
    return {p,vao,uniforms};
  }
  const fieldProgram=program(fieldFragment),markProgram=program(markFragment),rippleProgram=program(rippleFragment);
  shaderObjects.forEach(s=>gl.deleteShader(s));
  function target(w,h,float=false) {
    const texture=gl.createTexture();gl.bindTexture(gl.TEXTURE_2D,texture);
    gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MIN_FILTER,float?gl.LINEAR:gl.NEAREST);
    gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MAG_FILTER,float?gl.LINEAR:gl.NEAREST);
    gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_WRAP_S,gl.CLAMP_TO_EDGE);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_WRAP_T,gl.CLAMP_TO_EDGE);
    gl.texImage2D(gl.TEXTURE_2D,0,float?gl.RGBA16F:gl.RGBA8,w,h,0,gl.RGBA,float?gl.HALF_FLOAT:gl.UNSIGNED_BYTE,null);
    const fbo=gl.createFramebuffer();gl.bindFramebuffer(gl.FRAMEBUFFER,fbo);
    gl.framebufferTexture2D(gl.FRAMEBUFFER,gl.COLOR_ATTACHMENT0,gl.TEXTURE_2D,texture,0);
    if (gl.checkFramebufferStatus(gl.FRAMEBUFFER)!==gl.FRAMEBUFFER_COMPLETE) {
      gl.deleteFramebuffer(fbo);gl.deleteTexture(texture);throw new Error('Incomplete render target');
    }
    return {texture,fbo,w,h};
  }
  function dispose(t) { if(t){gl.deleteFramebuffer(t.fbo);gl.deleteTexture(t.texture);} }
  const blank=target(1,1);gl.clear(gl.COLOR_BUFFER_BIT);
  let field,read,write,width=1,height=1,dpr=1,pitch=9,cols=1,rows=1,origin=[0,0];
  let floatTargets=!!gl.getExtension('EXT_color_buffer_float');
  let rippleClock=0,rippleUntil=0,rippleLive=false;
  const pointer={x:0,y:0,lastX:0,lastY:0,inside:false,placed:false,burst:0};
  function draw(mesh,t,values,textures) {
    gl.bindFramebuffer(gl.FRAMEBUFFER,t?t.fbo:null);gl.viewport(0,0,t?t.w:canvas.width,t?t.h:canvas.height);
    gl.useProgram(mesh.p);gl.bindVertexArray(mesh.vao);
    textures.forEach((texture,i)=>{gl.activeTexture(gl.TEXTURE0+i);gl.bindTexture(gl.TEXTURE_2D,texture);});
    Object.entries(values).forEach(([name,value])=> {
      const u=mesh.uniforms[name];if(!u)return;
      if(u.type===gl.FLOAT)gl.uniform1f(u.location,value);
      else if(u.type===gl.FLOAT_VEC2)gl.uniform2fv(u.location,value);
      else if(u.type===gl.FLOAT_VEC3)gl.uniform3fv(u.location,value);
      else if(u.type===gl.FLOAT_VEC4)gl.uniform4fv(u.location,value);
      else gl.uniform1i(u.location,value);
    });
    gl.drawArrays(gl.TRIANGLES,0,3);
  }
  function clearRipples() {
    if(read) [read,write].forEach(t=>{gl.bindFramebuffer(gl.FRAMEBUFFER,t.fbo);gl.clear(gl.COLOR_BUFFER_BIT);});
    rippleLive=false;rippleClock=0;pointer.inside=false;pointer.placed=false;pointer.burst=0;
  }
  function resize() {
    width=Math.max(1,layer.clientWidth);height=Math.max(1,layer.clientHeight);
    const mobile=width<=650;
    dpr=Math.min(devicePixelRatio||1,mobile?1:1.25,Math.sqrt(1.8e6/(width*height)));
    canvas.width=Math.round(width*dpr);canvas.height=Math.round(height*dpr);dpr=canvas.width/width;
    pitch=Math.max(4,Math.round((mobile?9:8)*dpr));
    cols=Math.ceil(canvas.width/pitch)+1;rows=Math.ceil(canvas.height/pitch)+2;
    origin=[Math.floor((canvas.width-cols*pitch)/2),Math.floor((canvas.height-rows*pitch)/2)];
    dispose(field);field=target(cols,rows);dispose(read);dispose(write);read=write=null;
    if(floatTargets) {
      try {read=target(clamp(Math.ceil(width/8),4,512),clamp(Math.ceil(height/8),4,512),true);write=target(read.w,read.h,true);}
      catch(_){dispose(read);read=write=null;floatTargets=false;}
    }
    clearRipples();
  }
  function render(t,dt,interactive,now) {
    if (interactive && read) {
      if(pointer.inside&&!pointer.placed){pointer.lastX=pointer.x;pointer.lastY=pointer.y;pointer.placed=true;}
      if(pointer.inside||pointer.burst)rippleUntil=now+3500;
      if(now<rippleUntil) {
        rippleClock=Math.min(rippleClock+dt*60,4);
        let impulse=(pointer.inside?Math.min(Math.hypot(pointer.x-pointer.lastX,pointer.y-pointer.lastY)/14,1)*.35:0)*.32+pointer.burst*.32;
        pointer.burst=0;
        while(rippleClock>=1) {
          rippleClock--;
          draw(rippleProgram,write,{tState:0,uTexel:[1/read.w,1/read.h],uSize:[width,height],uFrom:[pointer.lastX,height-pointer.lastY],uTo:[pointer.x,height-pointer.y],uRadius:65,uImpulse:impulse,uDamping:.975},[read.texture]);
          [read,write]=[write,read];impulse=0;
        }
        pointer.lastX=pointer.x;pointer.lastY=pointer.y;rippleLive=true;
      } else if(rippleLive)clearRipples();
    }
    const heading=20*Math.PI/180,light=200*Math.PI/180;
    draw(fieldProgram,field,{uSize:[width,height],uDpr:dpr,uOrigin:origin,uPitch:[pitch,pitch],uWave:0,uTime:t,uUnit:580,uHeading:[Math.cos(heading),Math.sin(heading)],uAmp:1,uDepth:.95,uLight:[Math.cos(light)*.78,Math.sin(light)*.78,.62],uShine:.8,uContrast:1.2,uInk:0,uOpacity:width<=650?.26:.34,uFade:0,uFadeSize:.5,uAppear:1,tRipple:0,uRipple:rippleLive?.32:0},[rippleLive?read.texture:blank.texture]);
    const color=[.60,.62,.80];
    draw(markProgram,null,{tField:0,tAtlas:1,uOrigin:origin,uPitch:[pitch,pitch],uGrid:[cols,rows],uPattern:0,uMarkSize:.95,uStroke:Math.max(1.1*dpr,pitch*.08),uColor:color,uAccent:color.map(c=>c+(1-c)*.55),uBackground:[0,0,0,0],uAtlas:[1,1,0]},[field.texture,blank.texture]);
  }
  function locate(e,burst=false) {
    if(e.pointerType!=='mouse')return;
    pointer.x=e.clientX;pointer.y=e.clientY;pointer.inside=true;
    if(burst)pointer.burst=1.2;
  }
  return {resize,render,locate,clearRipples};
}
function moving(){return !!engine&&!lost&&!leaving&&!document.hidden&&!reduce.matches&&!userPaused;}
function stop(){cancelAnimationFrame(frameId);frameId=0;last=0;}
function tick(now) {
  // Keep the visible control in sync even if a media-query change is observed
  // by the frame before its change event is delivered.
  frameId=0;if(!moving()){sync();return;}
  const targetStep=innerWidth<=650?1000/24:1000/30;
  if(!last||now-last>=targetStep-1) {
    const dt=last?Math.min(.05,(now-last)/1000):1/30;last=now;time+=dt*.30;
    engine.render(time,dt,fine.matches,now);
  }
  frameId=requestAnimationFrame(tick);
}
function sync() {
  stop();
  const active=moving();layer.dataset.active=String(active);
  control.hidden=false;control.disabled=reduce.matches||!engine||lost;
  control.setAttribute('aria-pressed',String(!reduce.matches&&!userPaused&&!!engine&&!lost));
  control.title=(!engine||lost)?(english?'Static background: WebGL2 unavailable':'静态背景：WebGL2 不可用')
    :reduce.matches?(english?'Reduced motion follows your system setting':'已按系统设置减少动态')
    :userPaused?(english?'Play background motion':'播放背景动效'):(english?'Pause background motion':'暂停背景动效');
  if(active)frameId=requestAnimationFrame(tick);
  else if(engine&&!lost&&!leaving&&!document.hidden){if(reduce.matches)engine.clearRipples();engine.render(time,0,false,performance.now());}
}
function boot() {
  try {engine=createEngine();engine.resize();engine.render(time,0,false,performance.now());layer.dataset.renderer='webgl2';}
  catch(error){engine=null;layer.dataset.renderer='static-fallback';console.warn('Pattern Waves uses static fallback:',error.message);}
  sync();
}
control.addEventListener('click',()=> {
  if(control.disabled)return;
  userPaused=!userPaused;
  try{sessionStorage.setItem('eli-home-ambient-paused',String(userPaused));}catch(_){}
  sync();
});
addEventListener('pointermove',e=>{if(moving()&&fine.matches)engine.locate(e);},{passive:true});
addEventListener('pointerdown',e=>{if(moving()&&fine.matches)engine.locate(e,true);},{passive:true});
addEventListener('blur',()=>engine?.clearRipples());
document.documentElement.addEventListener('pointerleave',()=>engine?.clearRipples());
reduce.addEventListener('change',sync);fine.addEventListener('change',()=>{engine?.clearRipples();sync();});
document.addEventListener('visibilitychange',sync);
addEventListener('pagehide',()=>{leaving=true;sync();});
addEventListener('pageshow',()=>{leaving=false;sync();});
addEventListener('resize',()=>{if(engine&&!lost){engine.resize();engine.render(time,0,false,performance.now());sync();}},{passive:true});
canvas.addEventListener('webglcontextlost',event=>{event.preventDefault();lost=true;layer.dataset.renderer='context-lost';sync();});
canvas.addEventListener('webglcontextrestored',()=>{lost=false;boot();});
boot();
})();
