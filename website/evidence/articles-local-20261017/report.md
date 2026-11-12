# 实践文章板块与两篇文章 · 本地待审

- 范围：新增首页“实践文章”两行入口、中文导航“文章”、文章列表与两篇正文；原有视觉和动效保持。
- 本地版本：`475b995cfd9e5b56cdfe`。未部署，未提交搜索平台，无新增依赖。
- 数据：按用户要求加入贴近日常工作的假设测算，紧邻数字明确标识；未编造客户节省工时、准确率或经营收益。
- 真实经历来源：`content/projects.json` 的 P10（独立库存开发交付）、P09（主导扫码库存）、P36（团队客服项目，知识库整理、检索配置与测试）。客户名称使用现有匿名口径。
- 本轮只做中文正文；没有伪造英文对应页，文章页不显示失效语言切换。

## 阅读路径

首页底部实践文章 → 列表 → 正文 → 相关案例 → 返回文章案例段落 → 咨询。

## 验证

构建93个HTML页面、38个项目；全站链接、锚点、H1、隐私和HTTP检查通过。320/390宽度为真实浏览器的响应式模拟，不冒充物理真机。文章与关联案例返回、既有服务页返回、about#contact咨询入口通过。原有9个视觉/动效文件逐字节不变，原首页模板除新增板块占位符外相同。新增CSS无backdrop-filter或blur。

新文章与列表保持noindex,nofollow，未进入地图；地图仍88个原公开URL。生产的搜索开关未修改。

历史 `check_service_seo.py` 对服务正文、结构化数据和链接的断言通过，随后因其保存的20261016旧styles.css基线而失败；此历史脚本不计整体通过。本轮实际基线独立保存在baseline.json并逐项通过，未为消除旧失败改写历史证据。

## 文件与后续

- 编辑正文：content/articles.json。
- 模板与组件：scripts/articles.py、templates/article.html、assets/articles.css。
- 任务快照与截图：本目录before/、baseline.json、mobile-width-checks.json、desktop-article-list.jpg、desktop-home-articles.jpg、mobile-inventory.jpg、mobile-knowledge-estimate.jpg、mobile-consultation.jpg。
- 新建产物均用于本次审阅、回退和后续接续，保留，不清理。

当前用户授权只到本地审阅。后续如批准发布，应先复核正文、案例口径和测算标识，再按授权将publication_status调整为published、生成与核对Sitemap增量，并走既有发布流程；本轮不执行这些步骤。
