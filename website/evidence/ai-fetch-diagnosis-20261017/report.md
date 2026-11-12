# AI 服务页读取诊断 · 2026-10-17

结论：元宝可以在输入网址后自动提取并读取FDE服务页，上一轮“读不到”的判断已更正。Perplexity在本人完成平台安全验证后的新会话仍未读到正文，具体原因UNKNOWN。找到了不用安装的quark.sm.cn网页搜索，但未找到本站结果，不能代替夸克问AI验收。本轮未改任何线上文件、配置、视觉或动效，未重复提交收录，未安装软件。

## 元宝：已读，旧判定需纠正

仅向元宝发送带唯一diag标记的公开网址，未提供网页正文。元宝原生URL卡片取得当前标题，回答准确输出“初次沟通免费，实施服务低至500元起”等当前正文。源站记录4个同标记请求，全部200，返回压缩正文14399字节。

元宝将其自动取得的页面作为user_doc注入模型；模型因此称为“用户提供的正文”。上一轮仅按模型关于“没有独立打开”的自述判失败，证据不足。网页自动提取成功与模型是否另调浏览工具是两件事。此次能确认给定网址后的阅读，不证明无品牌自然推荐或独立搜索来源引用。

## Perplexity：读取仍未通过，未定位出可修的网站缺陷

1. 原生旧会话带diag读取返回Failed to fetch；源站未见该标记。
2. 改用site:www.eliai.cn/services/搜索，回答未返回本站服务详情页。
3. 新会话前遇到Perplexity自身Cloudflare安全检查，由用户本人通过。已登录免费方案，使用普通搜索和无痕新会话，不使用Computer或付费升级。
4. 新会话发送新的唯一标记，仍报告正文读取失败。源站未见新标记，也未见对应新增服务页请求。
5. 对照官方最新IP范围：原生PerplexityBot从已确认的官方IP访问过首页、robots、项目库和P13，均200；本机伪UA探测已单独标为非官方IP，不混算真实抓取。有限错误日志读取中没有匹配这些官方网段的错误。

这说明本次服务页失败尚未形成源站可定位的错误；不能据“无日志”断言厂商内部故障，也不能排除请求规范化、缓存、上游DNS/网络/策略等未取得的因素。没有证据支持改防火墙、DNS、TLS、重写网址、增加隐藏页或改视觉。Perplexity问题未解决，不以元宝成功或普通HTTP200替代验收。

## 网站侧对照

三个中文服务页均返回text/html和200；正文、标题与500元价格在静态HTML中，非必须JS加载；meta为index,follow；canonical为各自完整www HTTPS地址。robots对所有UA允许。客户端默认信任链核验两域名通过；本机DNS为代理fake-IP，不能用198.18地址当公网DNS故障，源站解析为117.72.148.45。

正式目录仍为20261017-toutiao-verification，157个公开文件全部匹配已发布manifest，Nginx配置哈希不变。没有构建或部署，也未安装、修改代理或关闭任何防护。

## 夸克：无安装替代入口的边界

https://quark.sm.cn/ 可在现有浏览器直接搜索。业务词首个结果屏未见本站；eliai.cn查询没有准确官网结果；site:eliai.cn原生提示没有相关结果。仅代表本次网页搜索观察，不是全量索引证明。

https://ai.quark.cn/当前跳转到https://www.quark.cn/客户端下载主页。quark.sm.cn页面是SM移动网页搜索，本轮未出现独立“问AI”交互；不能把该入口与夸克客户端的AI检索完全等同。按用户要求不安装，不再要求用户代做两轮问答。

## 原始证据与后续

- origin-marker-results.json：元宝唯一标记请求、Perplexity官方IP比对，已排除访问者IP和Referer。
- origin-after-fresh-control.json：新会话追踪和有限公开路径事件。
- service-html-check.json、origin-integrity-check.json、dns-tls-client.json：站点基础及零改动核对。
- yuanbao-marker-result.txt、yuanbao-read-success.jpg及perplexity-fresh-read-result.txt/.jpg：原生回答。
- quark-web-unbranded.txt、quark-web-domain.txt、quark-web-site-result.txt/.jpg：网页检索观察。

Perplexity需后续在出现新抓取/索引证据或平台可达变化后复测，不重复发送同一失败请求、不重复提交Sitemap。本次没有提交厂商反馈，也没有更改现有Google/Bing/百度跟进自动化。

官方参考：
- https://docs.perplexity.ai/docs/resources/perplexity-crawlers
- https://www.perplexity.com/perplexitybot.json
- https://www.perplexity.com/perplexity-user.json
- https://quark.sm.cn/
- https://ai.quark.cn/ （本次跳转官网主页）
