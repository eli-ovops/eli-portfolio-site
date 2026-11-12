# /cases/ 永久跳转生产修复（2026-10-22）

已按本线程明确授权上线：`https://www.eliai.cn/cases/` 返回 HTTP301，Location 为 `https://www.eliai.cn/records.html`；跟随后项目库返回 HTTP200。Nginx 仅增加精确路由 `location = /cases/ { return 301 /records.html; }`，保留 `autoindex off`、现有 deny 规则和所有详情路由。

## 修改和回退

- 唯一生产配置：`/etc/nginx/sites-available/portfolio-domain-pending`。
- 配置修改前 SHA256：5570323d452fc558369ebe860076dea84ad4490bce7e7ed3dfcdad6b78e0f759。
- 修改后 SHA256：5eb89e90bbe3def108a216fcb86f3ce778ed9f9667b53a033975aa3cb6a91352。
- 服务端备份：`/srv/eli-sites/portfolio/backups/20261022-cases-redirect/portfolio-domain-pending.before.conf`。
- 原子替换前核对配置、全部公开文件与当前发布链接均未漂移；`nginx -t` 通过后，仅 reload Nginx 一次，没有重启 ERP、MySQL 或 Redis。
- 若后续需要回退，应先确认当前配置仍为本轮修改后哈希，再原子恢复本次备份、执行 `nginx -t` 和 reload；不覆盖其他人的后续配置。本轮未触发回退。

## 已完成检查

- 公网不跟随重定向：301 与目标 Location 正确；跟随后200，没有循环。
- 16 个中英文首页、项目库、P09/P10/P36 案例和三个服务页公网内容哈希与修改前完全一致。
- 另查两个实际文章目录与库存/知识库两篇文章的中英文版本，共6个地址，均200且哈希未变。
- 浏览器从 `/cases/` 实际进入项目库，打开P10再返回项目库通过；三个中文服务页标题和咨询入口均存在。
- 369 个服务端公开文件完全未改；视觉、动效、正文、元信息、站点地图及其日期未改。当前网站内容revision仍为cc132dc0e7da5cecf41d，本次是单独的配置修复。
- Nginx、ERP、MySQL、Redis 的 ActiveState 和 MainPID 与修改前一致；其他启用的站点配置哈希不变。
- 不重复搜索提交、请求编入索引或点击Google“验证修正情况”；GSC旧403记录需以后续自然抓取的原生报告观察，当前HTTP修复不等于报告已经清除。
- 所有本轮浏览器访问属于我们自己的上线QA，不计自然流量或客户咨询；没有发出邮件、电话或微信消息。

## 同类目录排查

从公开站点地图的294个URL提取全部8个父目录入口，各一次匿名HTTPS读取。中文和英文根目录均200；`/cases/` 已由本轮修复。另5个裸目录仍403：

| 目录入口 | 当前状态 | 可用的实际入口 / 后续候选 |
| --- | --- | --- |
| /articles/ | 403 | /articles.html（已核200） |
| /en/articles/ | 403 | /en/articles.html（已核200） |
| /en/cases/ | 403 | /en/records.html（已核200） |
| /services/ | 403 | 现有首页业务场景及三个服务详情页可用 |
| /en/services/ | 403 | 英文首页业务场景及三个英文服务详情页可用 |

这5个是没有栏目首页的目录入口，不等同于其下文章或服务详情被禁止抓取。本轮仅检查并列出，未扩展修改它们。未来可在明确授权后精确跳转到已有相应栏目，不开放目录列表，也不批量改正文或URL。

覆盖边界：完成全部站点地图父目录与22个真实页面公网哈希检查；未执行294页面的逐一HTTP全量爬取、全站移动交互复测或索引覆盖验收。无需为此次精确配置修复重建网站或修改CSS/JS。

## 本地证据文件

本目录中的authorization.json、preflight.json、nginx-before.conf、nginx-candidate.conf、nginx-config.diff、publish.py、remote-apply-reviewed.py、publish-result.json、public-postflight.json、article-entry-check.json、similar-directory-audit-before.json、browser-check.json、浏览器TXT/PNG和receipt.json均为本任务的准备/执行/验收原件，保留供回退与跟进。服务器临时配置通过原子替换成为正式配置，没有遗留用途不明的临时配置文件。
