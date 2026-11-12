# 个人网站公网发布记录 — 2026-10-07

用户授权：将当前个人网站部署到用户共用服务器，独立目录，允许公网访问。唯一执行 Owner：当前个人网站会话。目标为京东云 [REDACTED_HOST]，不是 RoxyChao 预览站；按当前服务器专项指南使用严格身份校验的 SSH/SCP。

- 入口：http://[REDACTED_HOST]/sites/portfolio/
- 项目库：http://[REDACTED_HOST]/sites/portfolio/records.html
- release：20261007-132028
- 独立目录：/srv/eli-sites/portfolio/releases/20261007-132028
- public 链接指向上述 release；首次发布无旧网站版本。
- 非公开 Nginx 配置备份：/srv/eli-sites/backups/20261007-132028/erp-trial.conf
- 归档 SHA-256：8217e20da86164f5748faf72b42786c787c518eb5f039f9ed4713194d29961a5

## 验证

构建及本地42页检查通过。只打包42个HTML及引用的CSS/JS/图片/字体许可，79个文件；无隐藏文件、链接、PAX或本机扩展属性。公网逐文件下载 SHA-256 与本地候选79项全部一致。源码、原始客户截图、未知路径返回404，目录列表403。健康记录返回本次版本。

浏览器公网首页、案例选择、RAG截图弹窗、关闭、项目库搜索库存返回2条已实际验证；移动视口核对无横向越界，已加载带src的图片无解码失败。桌面和移动截图见本目录。真实手机未在本轮测试。

ERP /login、/mobile/、验证码接口只读均200；服务 nginx、erp-trial active。未登录ERP或写业务数据。Nginx原配置保留，只添加/sites/portfolio路由，通过nginx -t后reload。

## 限制和回退

当前HTTP公网IP访问；未配置域名、HTTPS，也不承诺搜索引擎收录，原noindex保留。公开范围以用户当前整站发布请求为准，未伪称取得第三方版权证明。自有静态源不是Git仓库，无commit可报告，以全文件哈希和包SHA-256绑定本次版本；不擅自初始化Git或上传源码。实际模型/effort信息不可回读为UNKNOWN。

若本次入口故障：保留现场，仅移除此新增路由或在确认没有并发配置更改时恢复本次Nginx备份，通过nginx -t后reload；不恢复ERP数据库，不覆盖其他项目。后续更新上传新release并原子切换本项目public，保留旧release。不要用备份整个配置覆盖其他任务新增的变更。

部署脚本最后写receipt时有Path拼接TypeError，但切换和reload已完成；首先只读核实正确版本与服务，再仅补写receipt，没有重复发布。原失败脚本作为证据保留。未来执行不得照抄该首次发布脚本。

## 本任务文件

本目录下public/、tar.gz、release.json、file-hashes.json、public-checks.json、site.before.yaml、deploy.sh、desktop.jpg、mobile.jpg均为本次发布候选、备份或证据，继续保留。远端/root/portfolio-20261007-132028.tar.gz和项目deployment记录保留用于恢复核对。未清理用户文件或历史版本。
