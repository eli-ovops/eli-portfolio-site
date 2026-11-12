# 首击、快速返回与图片放大 · 发布验收

状态：PUBLISHED_ACCEPTED_INDEXING_DISABLED。用户本轮明确授权同步此批修复、保留视觉/动效、上线后核验搜索/筛选/返回且禁止收录。唯一发布 Owner 为当前个人网站会话。

发布 `20261012-212302-first-pointer`，内容版本 `374bf42e288f80f56bf7`；切换回执为2026-10-12T13:25:17.650442Z（北京时间21:25）。入口 http://[REDACTED_HOST]/sites/portfolio/；当前版本入口 http://[REDACTED_HOST]/sites/portfolio/?pv=374bf42e288f80f56bf7。

此次没有新的源码实现。真实本地修复原件位于first-pointer-20261012，包含首击失败/成功的事件记录、入场期间返回及图片点击对照。重建后的144个公开文件全部等于已验收的本地输出；构建、路径/隐私、双语、SEO/禁止收录和两个导航回归通过，见local-checks.json。

沿当前JDCloud117.72.148.45指南与site.yaml复用严格SSH身份/显式钥匙/固定known_hosts/禁agent；没有访问其他基础设施。只核钥匙权限600和服务器ED25519指纹/hostname，不读取密钥内容。只将可复现USTAR/gzip-mtime0静态包及manifest上传私有路径；144个成员、路径、类型、元数据、逐文件及整包SHA已核。包SHA为a1a83231a244af04c67d01b4c08419da844e7f26f77dbef6dd7dc883147e5bb8，11,154,412字节。

先preflight核对实际旧链接/配置/服务/容量，再review、upload和隔离prepare。备份在/srv/eli-sites/portfolio/backups/20261012-212302-first-pointer，目录0700、配置快照0600；上一版20261012-194514-return-zoom的144文件完整保留并复核hash。发布仅一次原子替换portfolio/public链接。Nginx配置SHA未变且未reload；ERP/MySQL/Redis active，PC/mobile入口200仅代表入口可用，没有ERP登录或业务验收。未改数据库、权限、DNS、HTTPS、备案或自动化。

公网102个HTML/CSS/JS/JSON/TXT文件精确匹配发布hash，84个HTML禁止索引；作品集robots仍Disallow:/，sitemap404，源码/私有材料404，cases目录403。没有提交任何搜索平台或开放收录。逐文件证据见public-checks.json，远端见prepare/switch/postcheck-receipt.json。

真实线上浏览器使用新版本入口，未清缓存：项目库入场首次点击客户分类9项，库存搜索2项P10/P09；进入P10立即点主图，2558px截图弹窗打开；文字放大入口同样打开；Escape关闭并归还焦点。浏览器返回保留分类、搜索、顺序和版本。进入P09立即点击页面返回，恢复同一条件并聚焦P09。无结果0、重置全部38项。英文390×844模拟视口的键盘放大、减少动态及VisualDemo标注保留，无整页横向溢出；模拟设置已还原。本轮不代表实体手机、所有浏览器、FPS或全站任意路径验收。

控制台本轮仅记录一个浏览器原生过渡主动取消的AbortError（skipTransition called），对应预期的取消行为，实际操作路径已通过；没有把它写成“零控制台错误”。原件browser-errors.json。当前发布回执/契约/控制文档已更新，历史附录逐字保留，最终核对见final-checks.json。

截图online-fast-image.jpg为最终线上弹窗，无共享标题覆盖。初始手机截图online-mobile-keyboard.jpg采到未稳定绘制，保留过程证据但不用于视觉通过判断；真实弹窗再次核对loaded/393px原图，稳定截图为online-mobile-keyboard-stable.jpg。浏览器原件browser-checks.json，新版首页输出标签保留供用户查看。

本目录约11MiB，记录本轮新建的包/清单、限域脚本、原文备份、检查/操作回执、截图、报告及最终receipt；均保留用于验收/恢复，不发布源码或证据。发布时本机余量7.3GiB/97%、服务器19.54GB空余，无扩扫或清理。当前旧页面需首次刷新或新版入口；不能把已打开旧文档误当本版。后续新批次、基础设施或收录变更仍需相应具体授权。
