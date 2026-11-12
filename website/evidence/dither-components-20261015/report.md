# Dither Veil 和组件第二轮升级 · 2026-10-15

状态：LOCAL_IMPLEMENTED_VALIDATED_WITH_OPEN_NAVIGATION_OBSERVATION。本地版本 `e2f873ead9c54daf4412`；未发布，未开放索引，用户视觉评价待反馈。

用户确认使用官方演示默认机器人底图；已替换关于页首屏右侧旧流程图。保留用户链接的 brightness0.02、levels3、ink#461b8e、paper#bf8e1b、rim#170b0b；rimThickness沿官方默认0。采用官方Floyd抖色算法和三段原GLSL，经比对逐字一致。原图、来源、许可与hash记录于 robot-source.json、upstream-preservation.json 和资产台账，未作为本人肖像使用。

## 组件映射

- About DitherVeil：鼠标揭示原图、离开恢复、点击或Enter有限波纹；减少动态静态显示。
- About/Home MagicBento：能力非对称网格、惯性倾斜视觉、按压扩散；链接命中区域不跟着倾斜。
- About Stepper：沿用三步内容，原生tab按钮及前后切换、方向键/Home/End；合并history.state保存当前步，减少动态展示全部内容。
- 项目库 AnimatedList：增加现有图片缩略图，无图保留项目代码；原生锚点键盘导航；继续沿用原筛选和返回来源Owner。
- 详情目录：原aria-current观察器驱动位置指示条；事实及关联入口视觉层级更新。
- GradientText：标题有限入场色彩扫动及指针响应，减少动态禁用。

全站沿用静态生成、本地GSAP。此为适合现有技术栈的原生适配，不是把整个React组件库或React运行时直接装进网站。首页已完成的PatternWaves和CircularCarousel保留。未修改客户案例事实、咨询目的地、搜索和返回来源代码或截图查看器。

## 验证

构建84HTML/38项目；内部链接/锚点、双语42+42、SEO/noindex、JS语法及五份现有交互回归均通过。`check.py`内固定date字段为脚本历史字段，执行日期以本回执为准。原始输出见check-runs.json。

真实IAB检查包括：机器人静态/揭示/恢复及按钮Enter；三步切换/键盘/返回；库存搜索+网站分类得2项，P10关联P09返回保留条件；清除后进入详情返回38项；截图背景hidden锁定和Escape；环形轮播切换及P09返回；中文390及英文320模拟视口、减少动态完整内容和咨询定位。行为抽查版本e64050e2d308f8cdefb2，最终版本仅新增来源NOTICE与资产台账，功能文件相同；最终版本已刷新核WebGL2、无横溢和Enter揭示。真实截图见同目录PNG。

## 开放观察和限制

快速browser Back后立即点击页头关于，曾有一次首击未导航、第二次成功；根因未单独复现/定位，本轮不能宣称快速跨页零问题，留作后续专项。控制台曾保留已修复的english变量错误旧hash，以及skipTransition的AbortError；不宣称零控制台错误。

未验实体触屏/iOS Safari/全浏览器/FPS；未强制验WebGL不可用或上下文丢失。84页全量是结构和链接覆盖，不等于逐页视觉验收。完整范围、截图和参数详见browser-checks.json。本轮无服务器连接/部署、无索引开放或备案操作。
