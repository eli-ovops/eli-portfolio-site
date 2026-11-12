# 快速清除筛选首击修复

仅本地验收，版本 `90eb1f389143fe026465`，未部署、未开放收录。

## 复现与收敛

桌面项目库搜索库存、选择网站与工具，进入P10后立即浏览器返回，输入无结果词并鼠标点击清除。旧版重复出现词仍在、0项记录；事件跟踪显示 pointermove 能到达按钮，而 pointerdown/mousedown/click 没有到达文档。不是清除回调执行后重新回填。原始证据见 native-events-before.json、events-with-scroll-before.json、failed-first-click.png。

单独改为即时滚动仍失败，此试验已撤销。减少动态模式下相同操作通过。进一步只在离开案例页的 pageswap 阶段取消“历史遍历到项目库”的原生页面快照，相同快速操作通过；不依赖延时重试或提前在按下时清除。

## 实现

templates/layout.html 的早期导航控制器新增 historyList 判定，仅 Back/Forward 到项目库时提前 skipTransition，避免旧快照短暂吞掉首击。正常进入案例、显式返回链接的共享标题过渡保持；GSAP入场、筛选和组件源码全部未变。app.js及assets/editorial.js亦未改，既有取消拖动、键盘和焦点连续性保留。

scripts/check_first_pointer.cjs新增生命周期回归，覆盖中英文、根路径/部署子路径、历史返回与显式链接、外部来源和无API场景。对修改前layout运行明确失败，对最终版本通过。

## 验收

最终无诊断脚本版本：桌面连续3轮快速返回→无结果词→首击清除均回到空词/全部38项；库存+客户筛选经过P10关联P09后返回仍为2项、原条件保留；键盘清除与立即分类后清除通过；清除后P10关联P04返回仍为全部38项。中文390px、英文320px模拟视口的快速返回首击通过，无横向溢出。详见browser-checks.json。

84页构建、内链、双语、SEO与六份交互回归通过。18个受保护源码哈希/字节一致，包含紧凑布局、无毛玻璃样式、背景和画廊、图片弹窗以及导航来源代码。临时事件跟踪已从模板移除。HTTP X-Robots-Tag为noindex,nofollow，SEO检查DISABLED。未访问服务器或部署。

范围为本地IAB Chromium与模拟视口；不作为实体触屏、Safari/Edge或所有历史首击问题的验收。历史快照在返回时取消，视觉入场和筛选动画仍保留。
