# 返回来源统一管理 · 2026-10-14 · 本地验收

已修复清除后经首页重进案例、旧条件复活的问题。本地版本05f7213ef85c4cd8a350；未发布、未访问服务器、未开放收录。唯一Owner为当前个人网站会话。

## 修改与原因

旧动效控制器按项目ID相同就借用全局上一次列表记录，重写返回链接；新导航控制器同时管理显式from/历史来源，形成两份来源逻辑。

从assets/editorial.js移除重复session来源写入和.back改写。保留阅读位置恢复、项目标题viewTransitionName、切换/入场/筛选/reveal的所有动画代码。assets/page-version.js为唯一来源写入者，保留本次from/当前案例history来源和合法关联传递；旧无from链接只有真实同源列表referrer与保存列表条件一致时才能兼容，忽略pv/return/参数顺序但不忽略实际搜索/分类差异。不删除全部session或较早案例历史，因此旧案例真实原来源仍有效。

## 验证

新增check_return_owner.cjs真实运行两个控制器，模拟旧库存session和首页入口。旧源码在“首页不得复活已清除查询”断言失败；修复源码通过。覆盖中文/英文/服务器子路径、显式/历史来源、清除后的列表referrer不借旧条件、匹配旧列表兼容。已有关联返回、版本隔离、首击、快速重置回归通过。

构建84页/38记录；静态链接/锚点/隐私404、双语与SEO检查通过，noindex,nofollow与robots禁爬保持。

真实本地IAB：库存/客户项目→P10→返回→无匹配词→清除(全部38)→首页P10→返回，仍空词/全部38。正常返回与P10→结果外P04刷新后返回保持库存/客户项目/2项，原始行P10焦点及211px定位恢复。更换查询为洁具访问同一P10，再三次浏览器返回较早P10并刷新，较早案例仍返回库存/客户项目2项。3轮快速清除恢复空词/全部38/search焦点。

英文320×740/减少动态：inventory/Client work关联P09返回保留2项，键盘清除后首页P10返回空词/All/38 projects，scrollWidth320，无横向溢出。媒体与视口覆盖已还原。实体触屏、iOS Safari/其他浏览器/FPS未验收。

## 保护与收尾

styles.css、motion.css/motion.js、editorial.css、depth-gallery、screenshot-viewer、app.js、项目事实JSON、页面生成器与本轮前hash完全相同。只改两个来源控制文件并新增回归脚本，dist按正常构建更新；docs/交付与验证.md与site.yaml记录本地新版本/本轮不发布边界，既有线上仍147597147401d66f13ca。

本目录保留before/assets两份源码、scope/checks/browser/receipt JSON、source.diff、local-result.png与本报告。均为本任务证据，不删除。原有静态检查脚本更新其既有evidence回执，旧日期常量不是本轮日期，当前证据以本目录为准。没有新依赖、Git、服务器操作、备案操作或其他业务恢复。
