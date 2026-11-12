# HTTPS 待批准方案

仅准备，未申请证书、未安装 Certbot、未配置443或防火墙。

对象：eliai.cn 与 www.eliai.cn；独立个人网站 Nginx 文件 `/etc/nginx/sites-available/portfolio-domain-pending`。不修改ERP虚拟主机、数据库、DNS、SSH、其他网站。继续 noindex/robots 禁爬。

1. 备份现有域名Nginx配置，确认443与云安全组状态。
2. 从Ubuntu软件仓库安装免费Certbot（服务器当前未安装），为个人域名建立单独的HTTP-01验证目录与精确路径。
3. 向Let's Encrypt申请含两个域名的证书；需要同意证书服务条款。申请信息为公开域名，私钥留在服务器不输出。无额外付费资源。
4. 证书签发并验证主机名后，按 `https-proposal.conf` 配置个人域名HTTPS及HTTP跳转；`nginx -t`成功后仅reload Nginx。若需要新增443入站规则，仅开放网站HTTPS。
5. 使用系统Certbot自动续期定时器及证书更新后的Nginx reload钩子，执行续期dry-run，记录到期日。
6. 同步域名站点canonical/hreflang/分享/结构化数据到https，收录仍关闭。实测根域名、www、中英主要页面、证书链与无混合内容；浏览器验证手机页脚及搜索/返回。验证失败恢复本次域名配置与链接，不改业务数据。

官方说明：https://eff-certbot.readthedocs.io/en/stable/using.html#webroot
服务条款入口：https://letsencrypt.org/repository/
