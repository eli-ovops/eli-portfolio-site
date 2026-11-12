# SEO 准备与自然流量实验

2026-10-07，执行者为当前个人网站会话。用户授权：审核期间先完成基础SEO，并尝试后续自然流量。此次仅本地实现和候选构建，不改公网配置、不开放索引、不提交搜索平台、不购买推广或工具。

## 当前已实现

- 84页（中文42、英文42）独立title与description；首页明确FDE/AI/业务系统方向，案例摘要沿用已公开的实际工作说明。
- 82个正常页面自canonical，中英文各自独立canonical，互相及自身hreflang，并有默认中文x-default。
- Person、WebSite及WebPage/AboutPage/CollectionPage JSON-LD，仅描述Eli作为个人作品集作者。没有伪造客户评级、公司归属、获奖、收入或把团队项目全归本人。
- Open Graph / Twitter 标题、摘要和URL准备完成，没有添加虚构社交账号或新的配图。
- 单一配置`content/seo.json`管理当前base_url及indexing_enabled。planned_base_url仅是待确认目标，不渲染成已开通域名。
- 82个正常页面候选sitemap在evidence/seo-foundation/sitemap-candidate.xml；404、搜索参数不进入地图，不编造lastmod。
- 当前保留noindex,nofollow和原robots抓取限制；无活跃sitemap，没有向搜索平台提交。日后启用索引时，构建自动生成真实sitemap.xml和robots的Sitemap引用。
- 视觉、文字正文、案例顺序、GSAP、联系人及原图未改。

## 启动前必须核实

1. eliai.cn域名是否已付款且注册成功，实名认证通过。域名实名审核不等于ICP备案。
2. 北京服务器个人网站的ICP备案状态，以及上线时的备案号展示。
3. 最终选择www或裸域名之一。确认目标域名DNS、HTTPS及实际页面已正常提供服务，再更改seo.json的base_url。当前base_url仍使用真实现有IP路径，不将未拥有的域名写成活跃canonical。
4. 对IP、裸域、www、index.html/目录首页的重复入口做适用的301规范化；不影响共用服务器ERP路由。
5. 获得当前开放索引和发布授权后，将indexing_enabled改true并构建、验证、发布。根robots.txt必须位于目标域名根下；当前IP下的子目录robots不能控制整个共用IP站点，不改ERP根robots。
6. 用户在Google Search Console / Bing Webmaster Tools中验证域名并授权相应配置，再提交网站地图。未创建账号或提交任何外部站点。

## 最小自然流量实验

开放收录当天记为D0，前30天作为第一轮观察窗口，不承诺30天一定收录、排名、访问或成交。

优先观察3组与现有案例对应的需求：

| 页面 | 中文意图 | 英文意图 |
|---|---|---|
| P09扫码库存 | 扫码库存系统案例、入库移库出库 | barcode inventory system case study |
| P10洁具库存 | B端库存管理系统开发案例 | sanitaryware inventory system case study |
| P12社媒自动化 | 小红书内容自动化工具、自动做图上传流程 | Xiaohongshu content automation workflow |

检索词只是实验候选，不是搜索量已验证的结论。P12真实全流程成功尚未补充，不能写成功率或发布增长；P10交付后全面使用尚未验证，不能写已产生ROI。RAG案例保留本人知识库/检索配置/测试职责，不包装成全部独立开发。

每周记录：已索引页面、相关搜索词曝光、点击、排名变化和来自网站的有效联系。Search Console数据需真实账号回执；有效联系可人工记录来访者自己说明的来源，不把猜测当归因。排除自己测试和付费推广。未安装统计脚本或第三方追踪。

- 没有索引：查抓取/索引状态，不能把它归因于市场无需求。
- 已索引但无相关曝光：核对搜索意图及案例内容是否充分。
- 有曝光但少点击：调整准确标题和摘要。
- 有相关点击但无有效联系：检查能力范围、案例证据与联系入口。

只按观察到的证据迭代；第一轮不批量生成低价值SEO文章、不买外链、不发虚假评价。站点收录、实际访问、有效询盘和商业成交分别统计。

## 验证与交付

- `npm run build`：84页面。
- `python3 scripts/check_seo.py`：84独立标题/摘要，82正常页schema JSON、自canonical/双向hreflang，正文未改变，保持禁止索引；未来域名配置只读dry run通过。
- `python3 scripts/check_localization.py`及`python3 scripts/check.py`：双语/资源/链接/H1/隐私边界通过。
- `node scripts/check_app_locales.cjs`：中英文运行时初始化通过。
- 浏览器实读中文/英文首页、RAG案例head元数据通过；未改变body/CSS，无新增设备交互风险。
- 候选`evidence/seo-foundation/seo-prepared-static.tar.gz`仅公开HTML及引用资源，无源码/证据/配置/隐藏文件，USTAR无PAX，全包逐文件哈希校验通过。候选未上传服务器。

此次创建/修改的源码、配置、测试、before备份、检查JSON、候选地图、浏览器读数、归档及哈希均保留。未清理旧素材、版本或用户文件。构建更改dist，不等于已更新公网。实际公网版本见同目录public-state-readonly.json；后续发布不能直接复用含旧IPcanonical的候选，需要先更新最终域名并重新构建。

参考：[Google双语版本标注](https://developers.google.com/search/docs/specialty/international/localized-versions)、[Google站点地图指南](https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap)、[Google AI搜索基础](https://developers.google.com/search/docs/appearance/ai-features)。

## 2026-10-07 公网同步

用户随后明确要求更新服务器，基础元数据已发布至20261007-144516，121文件公网哈希核对及浏览器元数据检查通过。保持noindex，候选地图未公开/提交。详见 `evidence/seo-foundation/deployment/report.md`。此前本地阶段的记录保留，当前发布状态以此补充为准。
