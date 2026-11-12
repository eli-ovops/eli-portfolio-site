# 手机阅读与案例发现修复 · 2026-10-10

用户明确授权本地实施，保留蓝紫深色视觉、字体、GSAP堆叠与过渡；不发布。Owner：01a123a8-16ae-76f0-85c9-8e017dd95758。

## 结果

1. 项目库分类容器收缩并局部横滚；手机案例目录限制宽度、grid子项允许收缩。390px视口复现修复前中文records文档宽540px、英文P10宽550px；修复后内容宽375px（视口含15px滚动条），无整页横移。不用body overflow:hidden掩盖正文。
2. 手机<=650px的堆叠图库按当前卡片实际高度展开，ResizeObserver跟随过程展开/收起与语言文字长度。caption无内部滚动，手机wheel/touch不拦截页面滚动；项目标签、前后按钮、方向键和GSAP图片/文字过渡保留。桌面原区域滚动模式保留。
3. 七项首页代表项目新增中英“完整案例 / Full case study”链接；截图放大、摘要展开保留。
4. 客户属性与产物category分离：复用关于页既有九项客户ID集合作为共享常量，生成data-client；客户筛选包含P09/P10，同时网站与工具分类仍保留这些记录。未新增客户验收/采用声明、未改38记录文案/顺序。

## 必需验证（本Owner执行）

- python3 scripts/build.py：84 HTML / 38记录 PASS。
- python3 scripts/check.py：84页链接、锚点、HTTP与隐私公开边界 PASS。该既有脚本结果中的date/version为硬编码旧值，仅把本次运行结果引用为10-10检查，不当发布日期；原输出evidence/static-checks.json。
- check_localization.py同一断言逻辑，输出定向到本批次localization-checks.json：42中文+42英文、无残留中文访客文案、语言路由及资源 PASS；未改脚本源。
- node --check app.js / assets/depth-gallery.js PASS。
- 实际IAB模拟320/390/768/1280，中英首页/records/about/P10共32组合：document.scrollWidth <= document.clientWidth，全部PASS。
- 中英库存搜索+客户筛选均P09/P10两项；英文重载筛选恢复；类型筛选仍可得到这两项。
- 中文P10展开caption height=scrollHeight=497，gallery/card高747；鼠标位于手机阅读区滚动，页面y896→1104且项目保持2.000，无内部滚动/误切。
- 英文P10展开caption overflow=visible，gallery862/card861；中英完整案例实际跳转cases/p10.html及en/cases/p10.html。
- 桌面堆叠启用、区域模式保留，ArrowRight完成切换到P36；减少动态后7卡均可访问、7链接保留、gallery无残留固定高度；已恢复临时视口/媒体模拟。

截图：mobile-client-filter.jpg、mobile-expanded-story.jpg、desktop-case-link.jpg。详细读数browser-checks.json；源diff为source.diff；7项实际源码修改在scope/before可追溯（另备份未改localization.py）。当前治理入口两份的before也保留，历史附录逐字保留。

## 边界与收尾

本轮没有发布、SSH/DNS/SSL/备案写入、安装依赖、Git动作、新增客户材料或联系方式改动。未进行真实手机触屏、弱网、Safari/FPS或其他案例原系统核验；本地QA不等于用户视觉确认。基于10-09本地批次，生产仍按历史发布回执分层。

原服务已停止；按原scripts/serve.py恢复同地址4178，session99379；错误页data导航被策略拒绝，未访问或绕过它，在同IAB同原HTTP地址通过支持的新标签流程取得页面。旧错误标签未删除。

新建文件均位于本批次evidence目录，来自本轮源码/控制文档备份、浏览器证据、差异与验收记录；均为后续复核/恢复交付物，保留。无一次性中间文件，无清理操作。dist原约12MB，本轮限域统计dist约12MB、本批evidence约380KB；没有扩扫其他项目。

当前运行模型/effort/Fast UNKNOWN，无本次平台运行回执，保持客户端设置；不因此阻断已授权本地可逆修改。
