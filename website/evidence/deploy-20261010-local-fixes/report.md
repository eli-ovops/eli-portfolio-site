# 个人网站同步发布 · 2026-10-10

状态：已上线并完成本次必要验收。用户当前明确授权“同步上去吧”，覆盖此前只本地边界；其他业务保持暂停。
Owner：01a123a8-16ae-76f0-85c9-8e017dd95758；沿 website-delivery-sop P6-P11，DS-002B SHA256未变化；ROUTING-2026-09-30-v3，实际model/effort/速度UNKNOWN，未更改设置。

新版 `20261010-223517-portfolio-local-fixes`；入口 http://[REDACTED_HOST]/sites/portfolio/ 。输入为已验本地editorial-return-motion-20261010及此前所有本地修复。同步包含手机布局/滚动、完整案例/分类、案例证据与AI拟写标识、首屏/排序/社媒图标、文案精简、画廊直接滚轮/返回状态/截图入口、关于页和项目库返回动效。

## 发布与保护

- 只上传dist公开白名单143文件/84HTML；包约11MB、展开约13MB；USTAR普通文件、无隐藏/越界/链接/PAX/xattr。社媒图标LICENSE.md仅作为精确版权许可条目允许，未开放任意Markdown源码。
- 包SHA256：7e129d4d1ba3af4e6e07473c2fe6bcbef31b6138cd791ece75bf52476cfa30ca；本地成员哈希、上传后包SHA、远端所有143成员哈希一致。
- 独立新目录 `/srv/eli-sites/portfolio/releases/20261010-223517-portfolio-local-fixes`，先隔离验证后原子替换public符号链接；旧目录 `/srv/eli-sites/portfolio/releases/20261008-200047-technical-content`完整保留。
- 备份 `/srv/eli-sites/portfolio/backups/20261010-223517-portfolio-local-fixes`含原Nginx配置（600）和旧版文件哈希。Nginx配置SHA256前后均f8feed3d72ef606d90674a633f73a9449a31a874197e823130ed9b3b9d213445；无配置修改/reload/ERP重启。
- SSH严格固定身份/host pin匹配guide；没有复制或输出私钥/凭据，未访问数据库、DNS、HTTPS或备案。
- 为避免返回访客使用旧缓存，scripts/components.py增加9个CSS/JS引用的内容hash版本参数。未改这些资源内容/动效参数；本轮重新构建和双语/静态检查通过。

## 验收

- 本地84页构建/链接/资源/片段/H1/隐私/源码404，以及42对双语通过。脚本固定date/version不是本release标识。
- 公网98个HTML/JS/CSS/JSON字节SHA256与发布包一致；源码/原客户图片404，目录403（autoindex off），无文件列表暴露。最初检查错误地要求目录404，修正为403/404均不可列表后重新留存回执，未修改Nginx。
- 公网真实浏览器：展开01后图片滚轮切到02，页面位置保持；RAG详情返回保留02/展开；6图片实际已加载。
- 关于与项目库首次/Back返回动效采样连续变化；最终返回样本各60个不同transform，实际URL和标题核对后记录。初次过快批量导航采样落在非目标页而超时，未计通过，未因此修改网站。
- 客户分类+库存搜索2项，进入P09返回保持分类/词/结果；英文390px首页/关于无横溢、page滚动模式；英文手机选中RAG图片完整加载。
- 切换后服务器指向新release，ERP/nginx/mysql/redis active；ERP PC/mobile入口200，与发布前一致。未操作ERP业务或将200视为业务验收。

## 回退与限制

必要回退只涉及本项目public链接，旧目标为 `/srv/eli-sites/portfolio/releases/20261008-200047-technical-content`；执行前核当前状态并按具体回退授权处理，不回滚ERP或业务数据。

手机为模拟视口；实体机/iOS Safari/FPS、全38案例视觉、外部社媒与联系方式送达、域名/HTTPS/备案结果仍不在本次验收范围。未称用户/PMO正式业务验收完成。

## 保留产物

本目录before/、plan.json、prepare-remote.py/switch-remote.py、prepare-receipt.json/receipt.json、发布tar、package-manifest.json/manifest.sha256、cache-version.diff、static/localization/public/browser检查及online.jpg用于发布追溯与回退，保留；dist为必要构建。未清理源码、素材、备份或旧release，无无用途一次性文件。
