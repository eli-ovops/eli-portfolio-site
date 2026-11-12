# 首页规范链接修复：已上线并验收

官网revision：ee333e5fb82b7096a06c。一次原子切换，旧版本保留于/srv/eli-sites/portfolio/domain-releases/20261021-stable-urls-cc132dc0；Nginx未修改或reload，已发布的6条目录301保持，其他服务状态/PID与IP预览未变化。

全部369个公开文件在隔离目录、切换后各自校验；36项独立HTTPS文件哈希通过，含六个站长验证文件；6条目录跳转复核通过。包仅沿用当前线上公开文件清单，不发布源码或旧预览残留。备份、前置状态及包哈希见preflight.json、plan.json、validate.json、publish.json和receipt.json。

首页href统一为/和/en/；保留锚点、功能参数与嵌套from，旧首页兼容清理为客户端history.replaceState，不是新增HTTP301。中英文语言切换保留project和return，案例返回选中案例，列表筛选q及return逻辑保持。文案、CSS、媒体和动效代码不变；294页导航真实变更对应lastmod为2026-10-22。

浏览器原件browser-check.json及browser-*.txt记录中英文切换、首页→P36→返回、旧英文首页携带project/return/hash、中文库存筛选→P10→返回以及中英文咨询入口。一次快速连续语言点击未离开中文页，已如实保留；核新DOM后下一次点击实际到达正确英文地址，其他必需路径也实际完成，不把未变化观察记为通过。公网校验脚本最初误把站长验证HTML当普通网页要求版本号，已限定六个验证文件只核原始哈希；最终36项通过，无网站修正。

未重复提交搜索平台、请求索引、验证修复或发邮件。所有访问和咨询入口点击为本人QA，不算自然曝光/点击、客户咨询或成交。生产部署不代表Google旧403报告已消除或已新增收录/排名/引用。未做手机真机测试。
