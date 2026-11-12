# 首击与快速连续浏览修复 · 2026-10-12

状态：LOCAL_ACCEPTED_NOT_PUBLISHED。唯一 Owner 为当前个人网站执行会话。当前本地内容版本 `374bf42e288f80f56bf7`；线上仍是上一轮 `20261012-194514-return-zoom` / `c2eb30e0505c4396515b`，本轮未操作服务器。

范围：续接上一轮发布验收中明确保留的“快速首击未响应”样本。使用 systematic-debugging、verification-before-completion；先复现和事件追踪，再做最小修复。没有新依赖、业务内容、媒体、画廊规则、收录或基础设施变更。

## 原始证据与原因

1. 首页进入项目库后，立即点“客户项目”，页面已 DOMContentLoaded/pageshow，却未收到按钮 pointerdown/up/click，仍为全部。稳定态点击正常。筛选按钮本身没有入场位移；状态更新为同步代码，不把它归咎于分类实现。隔离副本只设过渡层 pointer-events:none 仍出现漏点，这个尝试没有保留到源码。
2. 案例标题过渡期间立即点“返回”，点击实际落在 HTML，留在详情页；原生过渡 active，根节点仍使用整页 root 快照。把编辑页的快照限制为 project-title、过渡伪元素透过点击后，真实返回生效，标题过渡仍 active。
3. 图片入场尚有遮罩时，pointerdown 落在 DIV、pointerup 落在图片链接、click 落在 DIV，弹窗未打开。视觉内容和命中区域共用移动/裁剪容器造成目标变化。稳定链接中的 visual span 接受原动画后，按下、抬起和点击均到达同一链接，弹窗打开。

红/绿原件：red-navigation-first-click.json、green-source-only.json、red-fast-case-back.json、green-fast-case-back.json、red-fast-image.json、green-fast-image.json。transition-hit-trace.json、green-fixture-first-click.json、green-departure-cancel.json 与 intermediate-* 保留过程和失败，不将中途成功或失败充当最终版本验收。

## 源码修改

- motion.js：仅对编辑页本来就要取消的非案例标题导航，在旧页 pageswap 时提前取消无用原生过渡；项目库↔详情的标题衔接及首页幕布保留。
- assets/editorial.css：编辑页不生成整页 root 快照，仅保留命名标题；快照伪元素透过点击。新增 visual span 的 display:block，最终排版不变。
- scripts/pages.py / assets/editorial.js：22 个中英文有图详情页的链接保持静止，原 opacity/y24/clip-path/.8s 入场改施于图片内容及说明；读者操作时完成尚在进行的入场和原生标题衔接，防止标题快照盖到截图弹窗上。未改变动画时长、曲线或默认视觉风格。
- scripts/check_first_pointer.cjs：验证中英文与子路径导航、标题衔接保留、首页幕布保留及缺失能力降级。

## 最终验收

最终源码构建84页/38项通过；静态路径/隐私、42对中英页面、SEO/noindex及导航版本回归通过。scope-checks.json 对上一轮已发布 tar 逐页核对：84页可见正文和所有 img 属性一致，22个稳定图片命中区域；项目资料、原图、app.js、主样式、画廊、截图弹窗代码、motion.css、页面模板及site.yaml保护哈希未变。source.diff 为四处相关实现的确切差异。

browser-final.json 对应内容版本 `374bf42e288f80f56bf7`：项目库快速首击客户分类9项；库存搜索2项P10/P09；入场立即点击主图打开2558px原图；Escape关闭并归还焦点；原生返回保留筛选/搜索/顺序/版本；进入P09立即点页面返回，回到相同条件并定位P09；空结果0及重置全部38项。英文390×844模拟视口、键盘放大、减少动态transform:none及VisualDemo说明保留，无横向溢出。手机模拟不是实体机或全浏览器验收，不声称FPS/性能测量或后台永久服务。

截图：local-fast-image.jpg 为最终本地截图弹窗，无共享标题覆盖；mobile-keyboard-dialog.jpg 为英文手机模拟。入场/标题默认动画没有因修复整体关闭；用户操作才主动完成未结束的动画。

## 收尾与产物

本目录均是本任务新建证据：probe.py、fixture/（上一版144个公开文件的隔离诊断副本，HTML含本地事件日志）、红绿/中间/最终JSON、源/文档备份、validate_scope.py、scope-checks.json、source.diff、两张截图、report.md、receipt.json。约14MiB，内置盘余量8.3GiB/96%；仅限本任务检查，没有扩扫或清理其他文件。隔离诊断标签已关闭，4179自有进程已停止；4178原预览继续运行。诊断副本保留用于复现，不进入dist/发布包。浏览器媒体/视口覆盖已清除，本地项目库结果页保留供用户查看。

当前收录仍关闭：84页noindex,nofollow，robots禁爬，sitemap未开放。后续服务器同步需新的明确发布授权。
