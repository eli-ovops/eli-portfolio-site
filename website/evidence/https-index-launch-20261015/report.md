# HTTPS与收录上线核验

入口 https://www.eliai.cn/ ，版本 0421d7822f14ab0f1f29。用户于本轮明确授权免费HTTPS及解除禁收录，依据同一Owner继续执行。

证书来自Let's Encrypt，包含裸域及www，默认CA/主机名验证通过，私钥600且未读出/下载。域名Nginx独立文件备份后变更，nginx -t成功并reload；ERP虚拟主机配置哈希不变。UFW原本未启用，公网443已有通路，未改防火墙或云安全组/DNS。自动续期timer enabled/active、真实staging续期dry-run通过、限定本证书的reload钩子单独运行通过。未来定时执行不作为已发生结果。

正式域名开放82页index/follow，2个404 noindex；robots Allow并声明HTTPS sitemap，82个URL全部唯一且无404/query，llms仅由已公开介绍/服务/问答同源生成。公网页面、robots、sitemap和英文首页默认TLS验证请求成功。IP预览维持原noindex/robots禁爬。

生产包从前一已发布域名版本转换head协议/robots/版本并生成发现文件，共140文件，逐字节核84页body只允许pv标识变化。未部署之前仅本地的项目库排版/名称改动；本地源码SEO配置已同步正式域名，当前本地版本4f7599a7fce500ff027c，用于后续正式域名构建。

浏览器HTTPS正常打开，搜索库存+客户项目2条，P10→P09→返回保留条件；快速Back后无结果首击清除恢复空词/全部38条。中文390/英文320无横向溢出。页面样式/动效控制器未改，实体手机、全浏览器与FPS不在此范围。

执行中两处脚本问题已纠正且保存首次失败：bootstrap生成的嵌套字符串换行先在远端解析时失败，未执行写入；之后增加本地AST解析。TLS reload后即刻探测443短暂refused，随后ss确认正常监听及CA验证成功；首轮包验证对404误要求canonical，已按既定404无canonical规则只检查正常页，失败发生于解包前，修正后通过。未通过的尝试不算验收。

回退点为 /srv/eli-sites/portfolio/domain-releases/20261015-165606-icp-footer 及 /srv/eli-sites/portfolio/backups/https-index-20261015/domain-before.conf。旧版本完整保留；回退仅本站域名链接和配置，保留证书/私钥及业务数据；新页面已合法允许抓取，回退不会撤销第三方已取得的公开内容。

实际搜索引擎收录、排名、GEO引用及搜索平台所有权验证/提交尚未进行；开放抓取不作为这些结果的证据。
