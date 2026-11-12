# Perplexity 三篇文章读取诊断

检查日期：2026-10-17。状态：未解决；原因 UNKNOWN。

## 结论

没有发现需要修改网站代码的已证实故障。此次三篇文章及首页对照在 Perplexity Search 中均报读取失败；普通 HTTPS 检查三篇文章均 200，正文为静态 HTML。源站日志在本次测试前后没有新增可验证的 Perplexity 请求，也没有诊断标记命中。该结果不能证明 Perplexity 没有尝试抓取，也不能区分 DNS、TLS、网络、缓存或平台策略。不得把模型给出的通用报错当成实际 HTTP 错误码。

## 当前证据

- 三篇文章：inventory-reconciliation、enterprise-knowledge-base、what-is-agent。完整 HTTP、标题、canonical、robots 和摘要哈希见 public-pages.json。
- robots 允许两种 Perplexity 代理。PerplexityBot 与 Perplexity-User 的官方 IP 范围分别保存于同目录 JSON。
- Google Public DNS DoH 当前检查：根域及 www A 均为预期服务器地址；AAAA 均 NOERROR 无答案。仅代表该解析器当前观测。
- 网站 Nginx 配置摘要仍为 5570323d452fc558369ebe860076dea84ad4490bce7e7ed3dfcdad6b78e0f759；此前已审阅的站点配置没有 WAF 或针对 Perplexity 的限制。本次未修改配置，云厂商上游过滤状况 UNKNOWN。
- 本次独立会话：https://www.perplexity.ai/search/1ecece57-5ea6-4a23-a7de-c75804b32e71 。Search 开、Computer 关。三篇文章及首页的带标记 URL 均失败。文本及截图见 native-retest*。
- origin-before.json / origin-after.json：当日当前 access.log 中，官方 IP 范围加 UA 验证的文章请求均 0，新增请求 0，标记命中 0。早先 PerplexityBot 的首页、robots、项目库及一个案例仍有 200 记录。
- 限制：全局日志没有 hostname；只看当前当日日志；服务端时钟比客户端慢约两分钟；请求可能被规范化、缓存或在源站前失败。测试参数时间后缀仅是唯一标记，不是测试时间。

## 官方支持的处理路径

1. 官方爬虫文档建议允许 PerplexityBot，WAF 存在时按官方 IP 范围加 UA 校验。Perplexity-User 是用户发起读取，通常不受 robots 限制。本站 robots 已允许，没有据此放宽安全规则的理由。
2. 官方支持已回复原工单，要求失败会话链接与逐字报错，可选截图和浏览器类型。自动收件确认和后续补充资料请求是两个不同回执，均不等于问题已修好或工程团队已确认根因。
3. 官方状态页检查时显示正常；不能据此排除单域名/单 URL 故障。
4. 已整理同一工单的完整补充邮件，见 support-reply-draft.txt。尚未发送、未创建新工单。无痕会话有 24 小时过期提示，因此应同时保留截图和逐字文字。
5. 已核对的官方文档未提供面向站长的强制抓取/重新收录接口；此次没有调用搜索平台提交，也没有制造镜像、改 URL 或重复提交通道。

官方来源：
- https://docs.perplexity.ai/docs/resources/perplexity-crawlers
- https://www.perplexity.ai/help-center/en/articles/10354894-how-do-i-submit-a-bug-report
- https://status.perplexity.com/

## 边界与下一步

本轮只新增本地诊断证据。网站内容、视觉、动效、Nginx、DNS 和生产发布均未修改。搜索提交 0；新增官方消息 0。

下一步：用户确认补充邮件后，在已有支持线程回复所需材料；等待明确的源站错误或官方可执行建议，再进行有依据的小范围修复。当前不能宣称 Perplexity 已能读取或自然推荐本站。

## 2026-10-17T19:10:34.888557+08:00

User approved the supplemental reply and screenshot. Sent once to [REDACTED_EMAIL] in the existing Gmail thread, with approved new body and attachment metadata read back. Gmail automatically appended the original support email quotation. See support-reply-send-receipt.json. No new ticket, website changes or search submissions. Root cause and resolution remain UNKNOWN pending support response.
