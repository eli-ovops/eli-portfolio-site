# 102 篇双语文章搜索表现复查

检查日期：2026-10-17；本轮只读，不提交搜索平台，不改网页、视觉、动效、DNS 或服务器。

## 当前结论

Google 已有可核实的文章收录进展：至少两篇中文文章已收录。不能据此认定全部 102 篇已收录，也不能把延迟的效果报表当成新文章的实际流量。Bing 四个检查样本仍未发现，效果报告准备中；百度索引数据计算中。

## 范围与证据

当前公开 sitemap.xml 返回 200，294 个规范 URL，其中中文文章详情 102、英文文章详情 102，无重复项、无查询参数。全量 URL 集合已核对；各搜索平台的完整文章索引清单尚不可得。本轮只读原生 URL 检查抽样四个地址/引擎，不能作为 204 个地址的全量收录统计。

今日此前已完成 204 个详情页加 2 个列表页的 HTTP/canonical/hreflang/标题/静态链接技术检查，原件为 ../articles-seo-geo-20261017/technical-checks.json。该全量检查没有在本轮重复运行。后续已授权发布只改 llms.txt，206 个文章 HTML 未变；llms 中英文文章入口已补上，旧审查中 llms_has_article_entry=false 是历史状态，不再是待办。

## Google

| 样本 | 本轮原生检查 |
| --- | --- |
| /articles/inventory-reconciliation.html | 未收录；Google 无法识别此网址，无抓取时间 |
| /articles/enterprise-knowledge-base.html | **已收录**；上次抓取 2026-10-17 18:43:42；Googlebot 智能手机版；抓取成功、允许索引；Google 规范网址为所检查的无参数网址 |
| /articles/what-is-agent.html | **已收录**；上次抓取 2026-10-17 19:39:32；Googlebot 智能手机版；抓取成功、允许索引；Google 规范网址为所检查的无参数网址 |
| /en/articles/enterprise-knowledge-base.html | 未收录；Google 无法识别此网址，无抓取时间 |

以上时间按后台原样记录。企业知识库中文页相较今日先前的“URL unknown”已有变化；Agent 入门页是本轮新增的索引样本，不能声称本次与旧 what-is-ai 样本是同一 URL 的状态变化。

收录详情记录了带 pv 的引荐网址，但 Google 当前选择无参数规范网址，未发现这两页的规范化错误。不要把引荐参数本身判成阻止收录。

效果报告：已应用网址包含 /articles/，同时涵盖中文 /articles/ 与英文 /en/articles/，不含文章列表。原生报告实际仍选择 3 个月，图表只有 2026-10-14 数据，上次更新提示 3.5 小时前，显示 0 曝光、0 点击、查询表无数据。此日期早于新文章上线，因此 **新文章上线后的曝光、点击、有效排名均尚不能从该报告判断**。不将平均排名 0 当成实际排名，也不声称已成功切到其他时间范围。

网页索引总览仍提示“正在处理数据，请过 1 天左右再来查看”，没有全量清单。站点地图显示 10-17 最后读取、88 个已发现网页、成功。这与线上 294 条及已收录样本存在更新不同步，不能用 88 推断只有 88 个页面可访问或要求再次提交。

原件：google-article-performance*、google-index-overview.txt、google-sitemap.txt、google-*-zh.txt、google-knowledge-en.txt、google-knowledge-indexed.png。

## Bing

搜索效果报告提示数据准备中、请 48 小时后再看；没有可用曝光、点击或关键词排名。不是“0 曝光”。Site Explorer 的 Indexed URLs 为 No data available，不替代全站索引统计。

同上四个文章样本原生 URL Inspection 的 Bing Index 均为 Not discovered / URL not known to Bing。没有点击 Request indexing，也没有运行 Live URL 抓取。

站点地图仍为 10-15 上次抓取，Success、82 个发现地址，错误与警告均 0；本轮没有再提交。历史 URL 提交已接受与站点地图发现 82 是不同口径，不能互相覆盖。

原件：bing-performance.txt、bing-site-explorer.txt、bing-sitemap.txt、bing-*.txt。

## 百度

- 索引量：当前全站规则 www.eliai.cn/，数据计算中；文章收录数 UNKNOWN，不能当 0。
- PC 近 7 天：全站 0 点击、0 展现；热门页面表无数据，无法单独核实这 204 个文章页的指标。页面说明当日数据约有 5 小时延迟。
- 移动搜索：没有可核实的数值或文章明细；记 UNKNOWN，不沿用 PC 的 0 值。
- 不新增后台目录规则、不运行需验证码的抓取诊断、不提交 URL/Sitemap，不打开令牌面板。

原件：baidu-index.txt、baidu-pc-performance.txt、baidu-mobile-performance.txt。

## 可以优化的内容（建议，未实施）

### 1. 为 sitemap 增加可核实的 lastmod

当前 294 个 URL 均没有 lastmod。不是协议错误，也不是已证实的未收录原因；但可以给搜索引擎提供实际内容更新线索。只使用逐页真实的最后重大修改日期，不使用每次构建/部署时间，更不能每天刷新日期制造新鲜度。继续沿用 sitemap.xml，不为这项建议新建或重复提交地图。

依据：scripts/seo.py 的 sitemap() 当前只输出 loc；线上 XML lastmod 元素数量 0。Google 官方说明仅在 consistently and verifiably accurate 时使用 lastmod，且应反映正文、结构化数据或链接等重大修改。

https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap

### 2. 改善少数过泛的文章摘要，按主题和具体练习描述

线上当前例子：
- Agent 要读文件、联网、发消息，都该允许吗？description 仅“权限要对应当前任务。”
- Agent 为什么要边做边检查？description 为“前一步错了，后面跑得再快也只是扩大错误。”

这些摘要不是重复标题故障，但脱离标题后不能说明文章教什么。建议将 meta description 与卡片摘要拆开：前者说清 Agent 权限、人工确认、停止条件或检查步骤，后者可保留现有简短文案与视觉。中英文分别核对，不机械增加字符或堆词。

需要先逐篇确认正文所含步骤再写最终摘要，不能凭摘要补出未经核实的承诺。本轮仅核查两个具体线上例子，没有断言 102 篇都有同类问题。Google 可自行从正文生成摘要，修改 description 不保证显示或提高点击。

https://developers.google.com/search/docs/appearance/snippet

### 3. 后续优先跟踪能带来咨询的问题，暂不据滞后数据重写全站

先跟踪库存人工核对、企业知识库资料准备、Agent 新手小任务及安全权限等长尾问题，并记录对应中英文落地页。出现真实查询后再判断有曝光无点击、排名低还是未发现；现阶段没有足够数据证明标题、价格或视觉导致流量问题。

这属于观测与内容优先级建议，不是关键词需求量或排名承诺。当前不建议继续堆文章、重复逐页提交、拆地图或为提高 GEO 编造客户效果数据。

## 本轮收尾

没有需要用户登录或验证码的步骤。网站修改 0、视觉动效修改 0、部署 0、搜索提交 0、外发消息 0。只新增本地审查证据。后续若数据覆盖上线日期后仍无新增发现，再按明确抓取/索引证据定位；本轮不为等待数据反复刷新报表。
