# eliai.cn 接入自己的服务器 — 2026-10-07

用户明确选择自己的京东云服务器，并要求先部署后备案。用户确认尚未ICP备案。文件/HTTP入口部署已经实施，不把技术可访问性报告成备案或合规验收通过。

## 已完成

- 新网正常页面确认域名注册及持有者实名认证成功。域名列表曾显示命名审核中，详情为ok，不能仅从订单支付推断注册状态。
- 确认原DNS只有两个默认NS记录。没有覆盖邮箱、既有网站记录或变更DNS服务器。
- 120个公开文件已上传到 `/srv/eli-sites/portfolio/domain-releases/domain-http-20261007`，`domain-current`指向本版本。原IP站点`public`保持20261007-144516。
- 保存原域名候选配置和原准备版目录；自己的Nginx域名配置为`portfolio-domain-pending`。当前已启用HTTP主机www.eliai.cn，裸域名转到www。没有修改ERP配置、数据库、现有服务端口或停止ERP。
- 所有120文件聚合SHA-256：0cfe3b3f21c4625d0654e777c0fa5711a41cc5341f07defd7f5255e09f2e8d2a。服务器内中文/英文首页及案例路径200，保留noindex，canonical目前是HTTP www域名。
- ERP PC、移动、原个人网站IP入口只读200。

## 当前必需用户操作

添加根域名A记录`@ -> [REDACTED_HOST]`后，点击保存触发新网短信“操作验证”。当下记录尚未落库，不能盲目重复提交。用户需在该弹窗内自行获取短信、输入验证码并确认；不用把验证码发到聊天里。确认A记录存在后，再添加www记录并核验公共DNS和实际域名访问。

当前没有www记录，没有成功域名公网访问回执。HTTPS未配置；服务器没有certbot。网站ICP备案未完成；不恢复或擅自开启搜索收录。

## 调试与保护

早期CAPTCHA iframe文字只是组件，不等于可见弹窗，已用实际截图纠正并通过正常导航读取页面；没有绕过验证码。此次DNS短信弹窗是实际可见的验证。

首次启用域名配置后，服务器内验证发现目录首页/index.html规则产生内部索引重定向，导致首页不是作品页面。先核实实际状态，没有重复发布；删除本次新增的两个index别名重定向规则并复测4路径通过。所有旧配置备份保留，只修改自己的域名配置。

新网赠送香港/北京体验空间均保持待开通；不购买或续费，不开启自动续费。上传仅网站公开产物，无源码、内部证据、证件或凭据。照片和客户原素材未改。

## 证据及生成物

同目录preflight、准备ZIP及manifest、prepare-own-server.py、候选conf、enable-domain-http.py、fix-domain-index.py、verify-domain-http.py、HTTP manifest以及dns-sms-verification.jpg用于恢复和继续工作，保留。远端/root/eliai-domain-ready.zip、准备版/HTTP版目录、候选配置、测试配置、备份和receipt保留。其他项目和历史媒体未清理。

同任务曾因默认cwd错误创建 `/Users/USER/Documents/eli/evidence/domain-connection` 空目录；确认是本任务新建且为空后已移除该精确目录，未处理其父目录或其他文件。

## 短信验证后状态

用户自行完成短信验证码后，根域名A记录已保存。随后www A记录正常保存，均117.72.148.45、TTL600秒，默认两条NS不变；Google公共DNS两域名均返回正确IP。新网操作回读截图dns-saved.jpg；没有修改其他DNS记录或账号安全设置。

浏览器实际打开http://www.eliai.cn/返回京东云“该网站暂时无法访问”页面，列明域名未在京东云完成备案等拦截原因。用户已确认未ICP备案，故当前域名访问阻断与备案接入一致。网站文件/HTTP域名主机已部署，公网域名访问仍未通过；不得报告已能正常访问。保存jdcloud-filing-block.jpg；未换端口、代理、Host、HTTPS或其他方式规避该公网拦截。

下一步为京东云网站ICP备案，获准后再核验域名正常页面及HTTPS。noindex继续保留，未开启自动续费或激活赠送托管主机。
