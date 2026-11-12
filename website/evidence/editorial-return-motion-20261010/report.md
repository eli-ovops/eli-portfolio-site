# 关于页/项目库返回动效修复 · 2026-10-10

批次 editorial-return-motion-20261010，Owner 01a123a8-16ae-76f0-85c9-8e017dd95758。仅本地，未发布。

## 原因与修复

用户指出两页标题动效再次不可见。真实浏览器读取 reduce=false、editorialStatus=ready、GSAP3.15.0，非脚本缺失。修复前采样证明首次访问两页 title transform/clip 连续变化；浏览器 Back 返回时均只有 none。源码 isReturning 统一跳过首屏动画，pageshow.persisted 也没有重播标题。

只改 assets/editorial.js：封装 playEntrance；关于页/项目库的标题、导语在首次和返回均保留原擦入/位移动效，BFCache恢复亦调用；原案例共享标题/列表阅读恢复规则保持，native-title分支不再清空这两页自己的标题动画。保持原0.8/0.76秒时长、ease、颜色、排版；未修改模板、CSS、内容、媒体、首页滚轮代码、依赖或服务器。既有指针/键盘/焦点操作仍可立即完成入场，减少动态保持静态。

## 证据

- 修复前 about-back-before、records-back-before 各60次动画属性采样只有一个值none。
- 修复后中文两页首次进入、浏览器返回，英文390px手机两页返回：各60次采样均有连续transform/clip变化；减少动态项目库60次采样仅none。采样不作为FPS测量。
- 关于页实际滚动1100→1650px，步骤03→06、进度条改变；项目库客户分类+“库存”搜索有2项，进入P09后原生返回仍保留分类/搜索/2项；首页展开后滚轮仍01→02，未重引入暂停规则。
- 构建84 HTML/38记录、84页静态/HTTP/片段/资源/H1/匿名与源码404、42对双语检查通过。检查脚本date/version旧固定字段不是本批次标识。
- about/records实际截图各5帧，约100/280/460/650/900ms；motion-replay.html仅回放这些真实帧，非完整录像或性能验收。截图900ms标题完全可读。

## 范围与限制

首次与普通Back返回已实测；本次IAB Back为back_forward新文档，BFCache persisted处理有代码覆盖但未实触发。手机是模拟视口，实体触屏/iOS Safari、FPS、全38案例动画未验。不将静态截图当完整动效证据。

before/、scope.json、source.diff、browser-checks.json、static-checks.json、localization-checks.json、两页10张jpg及motion-replay.html为必要备份/回归证据，保留；dist为必要构建，无无用途一次性文件或清理动作。
