# SEO / GEO 本地修复回执

日期：2026-10-20。状态：本地实现及验收完成，未发布。生产仍为 `fcafe9ca8a0e904465b2`；本地候选 `0670cd51cec094148791`。

## 本轮修改

1. 两篇英文教程 `ai-consultation-prepare`、`what-is-fde-business` 的正文“服务范围与咨询”来源链接使用英文服务页。共享来源保留中文 URL，并添加英文 URL；中文两篇不受影响，外部官方资料链接不变。
2. 294 个可索引页面的 Person.description 复用对应语言关于页已确认的前两段简介。人物介绍不再误用免费咨询与起价文案；姓名、职责、社交地址、邮箱和其他结构化字段保持不变。
3. `ai-ocr-check`、`workbuddy-spreadsheet` 两篇教程的中英文服务入口改为库存与流程服务，使用现有入口样式和标签。未改教程正文、标题、搜索摘要、案例或价格，也没有批量调整其他工具教程。
4. 本地状态契约 site.yaml 标记候选和待发布状态，保留生产版本与原发布授权记录，不把本轮“修复”当成新的生产部署批准。

未处理为代码修改：知识库实际问答证据仍需真实、可公开且脱敏材料，未编写效果数据；案例图优化暂未实施，保持原资源。

## 验证

- 构建 296 个 HTML、38 个项目记录通过。
- 现有 SEO 检查通过：294 个有效结构化图、中英文 canonical/hreflang、204 文章详情、标题与摘要、sitemap、llms.txt、案例和 FAQ 一致性。
- 本轮独立差异验证通过：仅预期 6 个文章页面的正文链接发生变化，其余 290 个页面正文（归一化版本参数后）不变；294 个结构化图只有人物 description 改变。遍历文章正文的站内服务链接，未发现中英文跨语言误链。
- 所有既有图片、CSS、JS、robots.txt、llms.txt 的构建产物哈希与本轮改前一致，无新增依赖、视觉或动效修改。
- 296 页本地 HTTP、站内链接、锚点、一个 H1、客户匿名与私有路径 404 检查通过。原脚本输出日期字段硬编码为 2026-10-06，本轮实际运行时间以 receipt.json 为准，不把旧字段当作本次日期。
- 浏览器模拟中文 360px、英文 390px：实际走通教程进入服务、英文服务进入案例并返回原服务、两种语言咨询入口、教程中英文往返；所读页面无横向溢出。仅浏览器模拟，不是真机检查，不发送消息或拨号。
- 两条英文来源链接用浏览器 DOM 核对实际 href 已为 `/en/services/fde-consulting.html`。这些来源链接按原设计使用公开绝对地址，因此本地验收未将点击线上来源当作本地修复已经发布。
- 保存手机正文来源区与咨询区截图；所有访问均为自身 QA，不代表自然流量或客户咨询。

## 旧检查限制

`check_tutorials.py` 的首页断言仍假设只有 2 个 article-row，但当前已发布轮播的改前与改后均为 10 个节点。`check_localization.py` 把翻译练习中有意保留且改前已有的中文术语样例判为漏译。两项不记 PASS，也未为让检查变绿改动无关内容；用当前改前快照、逐页正文差异、语言链接实测与本轮 scope-checks.json 检查本次回归。

## 更新日期

共享 Person 描述实际改变了全部 294 个可索引页面的结构化内容，因此内容指纹与 sitemap lastmod 按真实变更记录为 2026-10-20；这是人物元信息更新，不是重写 204 篇文章。文章可见撰写日期、资料核查日期、dateCreated/datePublished 与其他结构化字段均未改变。没有为了构建或部署刷新日期。

## 文件与边界

源码：scripts/seo.py、scripts/tutorials.py、content/tutorials/sources.json、content/tutorials/office.json、content/tutorials/workbuddy.json；生成 content/page-updates.json、dist 和既有 SEO 候选文件；site.yaml 仅记录本地状态。

验收入口：scope-checks.json、seo-checks.json、static-checks.json、browser-checks.json、receipt.json。改前源码和 296 页快照在 before/，用于复核与后续发布准备，保留不清理。

生产、服务器、DNS、SSL、robots、统计设置、搜索平台和邮件均未操作。未发布、搜索提交 0、索引请求 0、外发消息 0；本地候选不证明收录、排名、自然流量或模型引用改善。
