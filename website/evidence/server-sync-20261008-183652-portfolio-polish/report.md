# 个人网站发布回执

- 用户授权：2026-10-08「帮我更新到服务器上」。
- 发布版本：20261008-183652-portfolio-polish
- 入口：http://[REDACTED_HOST]/sites/portfolio/index.html
- 回退版本：/srv/eli-sites/portfolio/releases/20261008-090042-records-motion（完整保留）。
- 新版本：/srv/eli-sites/portfolio/releases/20261008-183652-portfolio-polish
- 包：20261008-183652-portfolio-polish.tar；SHA256：954f05479a20412b26bca1b6dcee429f995e3a02c4112acfdd2169d74405a036
- 84 个页面构建、资源/链接/隐私检查通过；137 个发布文件公网逐一 SHA256 匹配。
- 浏览器：首页项目图片、二维码、10 个社媒入口；英文项目库控制栏首帧可见、GSAP ready；375px 无横向溢出；中文移动应用筛选9项；关于我联系文案和图片正常。
- 真实浏览器截图：online-footer.jpg、online-contact.jpg、online-projects.jpg。
- ERP login/mobile HTTP200；Nginx 和 ERP active。未进行 ERP 业务登录或写入验收。
- 原子替换本项目 public 符号链接，无 Nginx/DNS/数据库/服务配置变更。
- 备案与 HTTPS 未在此次任务核验或修改；继续保持当前 noindex。
- 回退方法：核对 public 当前指向本版本后，用新的临时链接指向上述回退版本并原子替换；未执行回退。
- 本次生成物均在此 evidence 目录，用于发布恢复与审计，保留。
