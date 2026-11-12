# Pattern Waves 首页本地适配 · 2026-10-15

本地已验收，未发布。版本 `bf0ba763ee15b549be16`，视觉强度/风格仍待用户反馈。当前Owner个人网站会话；此前仅本地/不开放收录持续。用户明确指出上一版细线/柔光不符，并指定 https://reactbits.dev/backgrounds/pattern-waves 。

采用官方Pattern Waves四段GLSL，字节对比全部一致：passVertex、fieldFragment、rippleFragment、markFragment。来源文件 https://github.com/DavidHDev/react-bits/blob/e1bbb696fc53f7f91e694c529e4d68c899773b6e/src/content/Backgrounds/PatternWaves/PatternWaves.jsx 。源文件与许可证、SHA256存upstream及source-checks.json。官方组件依赖ogl，本站为原生静态站；本轮用本地WebGL2渲染/纹理/帧缓冲/生命周期适配，未引入React、OGL包或CDN运行资源。

许可证为MIT + Commons Clause：可作为网站组成使用，不能单独销售/分发组件或移植组件集合。完整许可证保存在assets/vendor/react-bits-pattern-waves/LICENSE.md，并在dist安全资产列表导出；JS头部保留作者/来源/许可证位置。不把许可证描述为无条件MIT。

修改：templates/home.html（canvas替换旧SVG）、assets/home-ambient.js/css、scripts/build.py（许可导出），site.yaml及既有交付记录；新增许可证。原主体文案、关于页、原GSAP、画廊/返回/弹窗、SEO等17份源码不变。前批次旧细线已退出当前首页，不扩展到其他页面。

实现：默认silk/dot核心，spacing8/9、深度.95、速度.30，蓝紫点阵与高光，desktop/mobile opacity .34/.26；窗口最大像素预算1.8M。原涟漪着色器以可用浮点帧缓冲运行；若不可用则保留基础布料波动。目标调度30/24帧不等于测得FPS。背景pointer-events:none，不拦截链接。手动暂停/系统减少动态/隐藏或离开页面停止rAF；返回时恢复，并在暂停时补一帧以恢复静态画布。WebGL2不可用/丢失时静态点阵退路，不冒充立体效果。

真实IAB：参考实际预览可见丝绸点阵与高光变化；首次公告关闭后只读浏览，无外部写入。本站WebGL2启动成功，移动与鼠标扰动的三张帧哈希不同；暂停时两张PNG哈希相同；Enter恢复。画廊01→02→01，P10进入及返回通过。中英文320/390模拟视口无横向溢出；系统减少动态后active=false且开关禁用。媒体切换首个en-320样本早于change回调，不作为稳态验收，后续en-390/zh-320样本已停止。模拟均已恢复，首页背景保持播放供用户预览。

检查：84页构建、静态/双语/SEO/JS语法、首击/返回来源/关联返回/搜索清除通过。官方四着色器与17保护源哈希通过，许可副本一致。shadcn组件审查清单已获取；React导入/TS/next/image不适用，本站无新增运行依赖。

未覆盖：实体手机/触屏、全浏览器、真实FPS/能耗、强制无WebGL2与上下文丢失恢复、浮点纹理不支持环境。截图和哈希支持画面变化/暂停，不能证明全设备流畅度。未部署、未开放收录、未改域名/备案/服务器。

产物：本目录before、upstream、source-checks、浏览器/多帧/暂停/手机截图、receipt用于复核与恢复，均保留。下载临时原件 /tmp/eli-pattern-waves-source.jsx、/tmp/eli-react-bits-LICENSE.md 与空目录 /tmp/eli-pattern-waves-oTAWlR 本轮创建，前两者来源为官方GitHub；原件已备份至upstream，收尾按精确路径及副本一致性核验后清理，结果见temp-cleanup.json。Jina Reader匿名401未重试/找凭据；沿已在用的官方网页/GitHub渠道读取原件，不宣称中介恢复。
