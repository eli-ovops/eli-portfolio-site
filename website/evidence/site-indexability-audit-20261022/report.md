# 网站本身SEO/GEO只读复核（2026-10-22）

结论：本轮没有发现类似目录403的新增硬性收录阻断。重点三个中文服务页、对应三个英文服务页与全部204篇中英文文章的技术信号通过。此结论不等于294页均收录，也不证明自然曝光或模型引用。

## 覆盖与证据

对公开sitemap.xml全部294个规范URL逐一匿名HTTPS GET：全部200，无跳转到其他正文；每页响应、HTML和SHA见pages.json与raw/。294页HTML哈希均与当前发布版本服务器基线一致。唯一初次采集异常为本地将/en/保存为目录文件的命名冲突，已修正证据保存并补采；不是网络错误或网站错误。

重点210页：204篇文章（102中文+102英文）和6个服务详情。全部自指canonical、index,follow、单个H1、标题和摘要存在，zh-CN/en自引用与双向对应正确；JSON-LD可解析；未发现完全相同的标题、摘要或整页main文本。这里不是语义质量、事实或近似内容全量重审。

robots.txt允许抓取；中英文文章目录均在原始HTML放入全部102个文章链接，JS分页只是渐进增强。全部204篇可沿原始HTML链接在首页3跳内到达，未发现孤立文章或缺失站内锚点。llms.txt已有两个文章栏目入口。重点页面使用的16个公开资源均200。三个中文服务页与一篇英文知识库教程浏览器抽查显示渲染后canonical及robots与原始响应相同。见rendered-samples.json及浏览器原始文本。

## 问题与优先级

| 优先级 | 证据与判断 | 最小下一步 |
|---|---|---|
| P1 取证跟进，非已证新故障 | 当日既有GSC“已抓取未编入索引”223行与本次204文章规范URL精确交集为167（中文85+英文82）。该历史表也包含随后已明确收录的库存、知识库文章，因此绝不能把167称为当前未收录总数。三个中文服务页今日已有原生收录证据，不重复检查。 | 等原生报告更新，沿现有任务轮换最多3条相关未确认样本，例如ai-knowledge-base-start、ai-inventory-exceptions、ai-cost-breakdown。根据新抓取和Google选定canonical再决定是否要改正文；不重复提交、不为告警取消canonical。 |
| P2 可选一致性整理 | 中文/en首页规范URL为/和/en/，但原始站内链接大多使用/index.html和/en/index.html；这两个别名目前200并正确canonical到根地址。本次共884处纯首页别名href，另6处带#needs。已有canonical正常归并，没有证据表明它们导致服务页掉索引。 | 如以后授权维护，可统一首页链接到根规范URL，并保持业务锚点及返回参数；不必为了它立刻上线，也不要贸然变更所有功能参数。 |

不建议新增一批行业页面、改服务URL、重复堆关键词、强行补字数或批量重写102个主题。本轮无证据支持这些作为故障修复。

## 官方判断依据

- https://support.google.com/webmasters/answer/7440203?hl=zh-Hans ：特定URL状态使用URL检查；“已抓取尚未索引”无需重新提交；有适当规范标记的备用页属正常归并。
- https://developers.google.com/search/docs/crawling-indexing/consolidate-duplicate-urls ：canonical及重定向用于统一重复URL，站点地图是较弱的规范信号。
- https://developers.google.com/search/docs/specialty/international/localized-versions ：双语版本应提供相互对应的hreflang。
- https://developers.google.com/search/docs/specialty/ecommerce/pagination-and-incremental-page-loading ：内容发现需可抓取链接；本站完整目录链接已在原始HTML中，不能只因下一页是按钮便认定文章不可发现。

## 边界

本轮未改网站源码/元信息/正文/视觉/动效/服务器，未构建、部署、提交搜索平台、请求索引、验证修复或主动模型提问。仅在证据目录保存公开抓取、诊断脚本和报告。所有访问属于我们自己的QA，不算自然流量或客户咨询。未重新检查GSC的204篇逐URL当前收录，不保证未受特定爬虫路径故障影响；没有真机、CWV现场数据或搜索排名结论。
