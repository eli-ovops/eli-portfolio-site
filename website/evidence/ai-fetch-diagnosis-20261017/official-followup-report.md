# 官方解决渠道续查 · 2026-10-17

结论：Perplexity 服务页读取故障仍未修复，原因 UNKNOWN；已确认官方支持路径并准备反馈草稿。夸克找到了无需安装、无需登录即可使用的官方 PC 网页搜索入口，但本次域名查询首屏仍未见本站。没有改网站视觉/动效、源代码、DNS、TLS、防火墙或生产配置，没有安装、没有再次提交地图或链接、没有发送支持反馈。

## Perplexity

当前原生会话仍明确说无法读取服务页正文。官方抓取指南区分搜索爬虫 PerplexityBot 和按用户请求读取的 Perplexity-User。本站现有全站 Allow 规则已允许它们；同日来源 IP 核验过的真实 PerplexityBot 成功读到首页、项目库、P13，不能称全站被拦。服务页请求未见于源站，不足以判定缓存、平台策略、DNS、网络或其他上游哪一个导致失败。

官方 WAF 放行说明只在有相关拦截时适用。当前无此证据，不增加宽泛的 UA 白名单、不关闭安全防护，也不为此加无依据的特殊页面或重复提交索引。用户已完成的是 Perplexity 自身安全检查，它与远端服务页抓取问题应区分。

官方后续路径：Help → Contact Support，说明浏览器和复现步骤，附合适截图；功能问题可联系 [REDACTED_EMAIL]。草稿 `perplexity-support-draft.txt` 只含公开网址、精简复现和脱敏结论。`perplexity-support-clean.jpg` 已收起账户侧栏。尚未发送；任何实际发送先取得用户对完整草稿及收件人的明确授权。

## 夸克

从 https://123.quark.cn/ 的搜索框查询 eliai.cn，打开 www.quark.cn 的原生结果页，不需要安装软件或登录。本次结果为10个网页链接，首屏未见本站。虽标题是“夸克AI”，画面是普通网页结果，不冒充已经验证“问AI”的生成回答或引用。此前 quark.sm.cn 的 site 查询未找到结果也只是有限样本，不等于完整索引证明。

官方神马 Sitemap 文档存在，并说明不保证抓取、索引和排名；本次没有找到更明确的官方承诺，能把神马提交等同于夸克网页/AI的必然覆盖。因此维持用户原先暂停神马注册的决定，不擅自注册、接受新条款或重提URL。

夸克官方帮助中心提供 [REDACTED_EMAIL]。`quark-support-draft.txt` 已准备咨询“官方站长入口、神马覆盖关系、可访问却搜不到的排查方式”，尚未发送，也未进行收录提交。

## 下一步

优先让 Perplexity 官方根据复现核对抓取状态；夸克先取得官方收录渠道与覆盖关系答复，再决定是否值得恢复神马接入。保持当前站点稳定，既有 Google/Bing/百度跟进继续按原流程执行，不为本问题反复推送。

## 官方依据

- https://docs.perplexity.ai/docs/resources/perplexity-crawlers
  - Separate PerplexityBot and Perplexity-User; allow robots and published ranges; WAF guidance is conditional, not a reason to add broad bypasses.
- https://www.perplexity.ai/help-center/en/articles/10354894-how-do-i-submit-a-bug-report
  - Official bug report route: Help > Contact Support; include browser, reproduction details and optional screenshots.
- https://www.perplexity.ai/en-GB/hub/security-vdp
  - Functional issues directed to [REDACTED_EMAIL], not vulnerability reporting.
- https://www.perplexity.ai/help-center/en/articles/10354884-cloudflare-vpns
  - Concerns access to Perplexity own UI; user already completed challenge. Does not diagnose remote website fetching.
- https://123.quark.cn/
  - Official navigation search opens www.quark.cn results in a new tab, usable without software installation or login for this query.
- https://www.quark.cn/documents/help
  - Official customer service email [REDACTED_EMAIL]; public help reviewed did not establish a separate Quark webmaster submission channel.
- https://zhanzhang.sm.cn/open/helpsitemap
  - Official Shenma sitemap documentation; says submission does not guarantee crawl, indexing or ranking. Does not establish guaranteed Quark AI coverage.
- https://zhanzhang.sm.cn/open/help
  - Official Shenma support email and help links; registration remains paused by user.
