# 静态网站同步 · 2026-10-15

已发布并完成技术核验。release `20261015-131729-records-catalog`，内容版本 `8b38e3e30012cfd1e243`，入口 http://[REDACTED_HOST]/sites/portfolio/records.html?pv=8b38e3e30012cfd1e243 。用户本轮明确要求上传当前本地网站；由本会话执行，仅作品集静态包、独立版本目录和public链接切换。

## 发布证据

只打包当前生成HTML、引用资产及必要静态入口，共138文件、6,776,525字节压缩包。USTAR、标准化mtime/uid/gid与gzip头，两次重打包字节相同；无PAX/AppleDouble/隐藏文件/源码/凭据。包SHA256为 `e85a44f5f5993997477e3086f2d22c7e125711aaa0222e05a03d0ad80ac5c07c`。严格SSH身份核验，先独立目录验包再原子切换public。当前远端138文件及全部138个公网文件hash一致，旧版 `20261014-133040-boss-consult` 的144文件完整保留。未引用的旧资产未复制进新版本，但旧版本原件仍在。

共享Nginx配置hash未变，无reload/restart或系统配置写入；ERP/MySQL/Redis/Nginx仍active，ERP PC/手机入口200。没有业务登录、业务数据或备案操作。84页仍noindex,nofollow，robots禁止抓取；sitemap及源码/私有配置路径404，目录列表403。

## 浏览器

线上桌面确认正确内容版本与双列目录；库存+客户筛选为2项，P10关联P09返回保留条件及原行焦点。单击清除、快速浏览器返回后立刻搜索无结果并首击清除均回到空词/全部38项。中文390px为单列、英文320px清除正常，未观察到整页横向溢出。首页画廊next/previous可切换；Pattern Waves画布已加载。关于页机器人等待图片加载/解码完成后为1400px素材和556×370画布，实际截图可见；初次未解码完成状态单独记录，不冒充成功。最终错误日志为空。

浏览器为IAB Chromium与模拟视口，不等于实体触屏、Safari/Edge或全站逐页UX验收。未开放收录，未改变域名/HTTPS/备案自动化。用户视觉认可和最终管局结果仍是独立事项。原始记录见receipt.json、public-checks.json、browser-checks.json及各阶段receipt。包和脚本为审计/恢复材料，保留。
