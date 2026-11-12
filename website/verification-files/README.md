# 搜索平台验证文件

Google、Bing、Yandex、百度、搜狗与头条 官方下载的公开网站所有权验证文件，已获用户授权放到 https://www.eliai.cn/ 根目录。不是账号密码、会话令牌或 API 密钥。

后续每次正式域名发布，必须在普通网页构建包之外，保留 manifest.json 所列根目录文件及原字节；不能用 dist 单独覆盖丢失它们。它们不放入站点地图，不参与网页标题/H1检查，不改变用户页面或动效。删除会使所有权验证失效，须另获用户明确授权。

本轮没有为接入验证而修改 build.py 或重新生成网页。部署记录：evidence/search-platform-360-sogou-20261016/receipt.json。

2026-10-17：仅新增头条 ByteDanceVerify.html，原156个正式文件字节不变，视觉版本 ef627aa38d38fa4ba886；头条所有权验证和首次Sitemap提交已返回成功。回执：evidence/toutiao-geo-20261017/receipt.json。
