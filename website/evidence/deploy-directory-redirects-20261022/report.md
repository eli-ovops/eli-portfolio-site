# 五个目录入口永久跳转：已上线并验收

仅在个人网站 Nginx 配置增加五个精确匹配301；保留原 /cases/ 跳转、autoindex off 和隐藏路径保护。未构建或切换网站文件。

| 目录 | 301目标 |
|---|---|
| /articles/ | /articles.html |
| /en/articles/ | /en/articles.html |
| /en/cases/ | /en/records.html |
| /services/ | /index.html#needs |
| /en/services/ | /en/index.html#needs |

5个新跳转及已有 /cases/ 均独立HTTPS验证301，跟随到200；22个中英文栏目、文章、案例及服务页200且哈希与部署前一致。服务器369个公开文件逐一哈希不变。浏览器13项观察覆盖5个落地栏目、文章打开、文章到案例、返回原文章、文章与服务语言切换及三个中文服务页。assets/仍403禁止目录列表；未开放目录浏览。

nginx -t通过，reload一次；其他站点配置与服务状态/PID保持。旧ERP已由用户另行停用，本次保持inactive，不启动。备份位置和配置指纹见receipt.json。

搜索平台提交、请求索引、验证修复、邮件发送均0。所有验收访问为本人测试，不能算自然搜索或客户咨询。Google历史403报告是否清除尚未核实，应等正常重新抓取，不宣称已恢复收录或排名。
