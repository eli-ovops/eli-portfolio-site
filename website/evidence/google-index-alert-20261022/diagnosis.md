# Google 索引邮件警报只读诊断（2026-10-22）

用户提供当日 16:04 的 Search Console 邮件，提示“备用网页（有适当的规范标记）”及“由于禁止访问 (403) 而被屏蔽了”。本次直接进入官方 Search Console 报告，没有访问跟踪邮件链接、下载外部邮件图片或修改邮箱。

## 原生报告

- 当前原生索引汇总：已编入索引 77、未编入索引 363。未收录分三组：备用 139、403 为 1、已抓取尚未收录 223。界面上次更新日期显示 2026/10/16，样本抓取日期存在 10/17；日期按原界面保存，不擅自推断数据完全截止或何时新增。
- 77 是全站网址口径，含旧参数 URL，不能称为 77 篇文章、77 个规范页面或本次新增长。
- 403 列表只有 `https://www.eliai.cn/cases/`，上次抓取 10/15；首次检测任务日期显示 10/17。并非 P10 详情或三个服务页。
- 139 条备用样本全部读取，139/139 含 `?pv=`。这是历史参数重复网址分组，不是 139 篇正文因质量处罚。Google 官方对此类别解释为指向规范网页的正常归并，无需为了让参数版本收录而取消 canonical。
- 223 条已抓取未收录样本全部读取，其中 48 条含 pv、175 条不含 pv；不是 223 篇新的独立文章。列表含三个中英文服务页，必须以逐网址的当前原生检查辨别旧汇总，不能据此断言服务页掉索引。

## 当前公开访问

`public-http-check.json` 为一次普通匿名 HTTPS GET 的回执，默认 TLS，没有伪装爬虫、Cookie、代理或绕过：

| 地址 | HTTP |
| --- | --- |
| /cases/ | 403，停止对该地址继续取回 |
| /cases/p10.html | 200 |
| /services/ai-agent.html | 200 |
| /services/workflow-automation.html | 200 |
| /services/fde-consulting.html | 200 |

本地当前源码和 dist 均无 cases/index.html 或 en/cases/index.html，未发现指向精确 /cases/ 目录的站内 HTML href。目录 403 与没有目录首页、禁止目录列表的表现一致，但尚未读取服务器配置或日志，具体服务器规则仍 UNKNOWN。当前普通 GET 成功不证明 Googlebot 抓取或索引，也不能将单一目录403扩大成全站被屏蔽。

## 最小后续建议（未实施）

若 `/cases/` 预期为案例目录入口，可只将该地址永久重定向至现有项目库 `/records.html`。这比开放服务器目录列表更符合现有信息架构；实施前仍需按用户当前“不改站”边界取得具体部署授权。不改三个服务 URL，不取消正常 canonical，不批量重提文章，也不点击“验证修正情况”或“请求编入索引”。

官方说明：https://support.google.com/webmasters/answer/7440203?hl=zh-Hans ，重点为 forbidden、duplicate_page_with_proper_canonical_tag 与 crawled-not-indexed。后者不要求重复提交。

本轮网站/服务器/搜索提交/索引请求/验证修正/邮箱修改均为 0。当前三个服务页的原生索引截图、文本及最终摘要见同目录 receipt.json。

## 后续服务器只读实核：根因已确认

2026-10-22 18:36–18:37（Asia/Shanghai），按当前共享服务器指南通过严格主机校验 SSH 完成配置与公开发布目录读取，未更改任何服务器内容。当前指南已更新同一钥匙的有效期；本轮没有修改授权、钥匙、代理或网络设置。

- 生效站点文件 `/etc/nginx/sites-available/portfolio-domain-pending` 的 26–30 行使用 `root /srv/eli-sites/portfolio/domain-current;`、`index index.html;`、`autoindex off;` 及 `try_files $uri $uri/ =404;`。
- 当前发布目录的 `cases/` 存在，但 `cases/index.html` 不存在；目录权限 0755、P10 文件权限 0644，均正常。
- Nginx 错误日志已找到同路径的明确原因 `directory index is forbidden`。仅返回匹配错误的时间和原因，没有返回或保存访客 IP 与整行日志。
- 中英文现有项目库 `/records.html`、`/en/records.html` 均返回 HTTP200，自指 canonical 正确。
- 因而当前 `/cases/` 403 的直接原因已由“推断”更新为“目录索引被禁且没有目录首页”。不是抽查的 P10 或三个服务页的权限问题，也不是本轮发现的服务器掉线。

候选最小修改仅针对目录入口：在相应 HTTPS server 块加入 `location = /cases/ { return 301 /records.html; }`，保留 `autoindex off` 和所有案例详情路径。此方案尚未实施，生产配置修改等待明确的修复/上线授权。
