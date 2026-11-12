# 双语版本实施及发布 — 2026-10-07

用户请求：完整英文版，点击切换。当前网站修改与公网迭代由当前会话执行；既有公网部署授权沿用同一目录和服务器。

## 实施

中文默认入口保留。新增en/下首页、关于、项目库、404及38个案例，共42页，整站84页。英文内容位于content/en.json，UI和构建本地化位于scripts/localization.py。没有新增框架、依赖或远程翻译服务。

导航右侧EN/中文链接对应同一页面；案例身份相同，当前页面hash由链接点击时保留。无JS也可以通过原生链接切换对应页面。英文页面使用lang=en，切换链接有lang/hreflang。共享相同真实截图，界面图片中的原始语言不修改。客户匿名规则和角色、团队、交付状态沿用原文；不新增成果指标。

共用app.js、depth-gallery.js、screenshot-viewer.js按页面lang输出英文搜索数量、案例标签、展开收起、截图弹窗及无障碍名称。英文长标题和小屏四项导航仅做局部字号/间距适配。中文外观和案例排序保留；404原先根绝对首页链接改为站内相对路径。

## 验证

- build：84HTML、38记录。
- scripts/check.py：84页H1、链接、锚点、本地HTTP、脱敏和源码边界通过。
- scripts/check_localization.py：42英文页正文和访客属性无汉字（语言切换“中文”除外），42组同页切换和所有英文资源/srcset通过。
- app.js、depth-gallery.js、screenshot-viewer.js语法通过。
- 浏览器：英文项目过程展开/收起、截图弹窗、英文inventory搜索2条、P10完整英文正文、中英文案例往返同页通过。
- 320x568、375x812、1440x900，英文首页/关于/项目库/P10共12布局无根水平溢出，已加载图片无解码失败。layout-checks.json有原始读数。
- 公网中文首页实际EN点击进入英文主页，桌面和手机模拟截图核对。真实手机未本轮实测。

## 发布

服务器117.72.148.45。同一独立项目目录原子切换，无Nginx更改或服务重启。

英文：http://[REDACTED_HOST]/sites/portfolio/en/index.html
中文：http://[REDACTED_HOST]/sites/portfolio/index.html
release：20261007-133421
SHA-256：d7c316b938faadf418e10e84eadf001e458ac8c775883f8709dc41edd82c249f
新版本：/srv/eli-sites/portfolio/releases/20261007-133421
保留回退版本：/srv/eli-sites/portfolio/releases/20261007-132028

公开产物121文件，USTAR/gzip确定性包，只普通文件，无PAX、本机扩展属性、隐藏文件、链接或敏感来源。全部121文件从公网下载，逐文件SHA与候选相同。英文源码JSON、构建脚本、内部资料和原客户图公网404。ERP登录、移动入口、验证码只读200；不写ERP数据。当前HTTP/noindex维持。

后续如需回退，在具体授权和当前public指向核对后，仅原子切回上述旧release；不修改ERP或数据库。首次发布的配置备份仍在独立非公开目录。源目录非Git，不虚构commit；以构建产物全文件SHA及归档SHA绑定发布。

## 文件及保留

本任务修改：scripts/components.py、pages.py、build.py、templates/layout.html、app.js、assets/depth-gallery.js、assets/screenshot-viewer.js、styles.css、site.yaml、README.md。新增content/en.json、scripts/localization.py、scripts/check_localization.py。before/备份、翻译写入脚本、检查JSON、布局JSON、release/候选及归档/部署脚本/公网检查、public-desktop.jpg和public-mobile.jpg均保留作复核或恢复。没有清理用户文件或旧版本。远端/root/portfolio-20261007-133421.tar.gz及deployment记录保留。
