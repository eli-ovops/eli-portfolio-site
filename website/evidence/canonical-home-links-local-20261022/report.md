# 中英文首页规范链接：本地验收通过，未发布

候选revision：ee333e5fb82b7096a06c

生成阶段统一全部页面中指向首页文件的href：中文/index.html→/，英文/en/index.html→/en/。保留原query和hash；#work/#main等纯页面内锚点保持原样。仅匹配本站两个首页，不改外站、资源路径或其他页面。

导航脚本兼容旧首页和嵌套from：保留已有业务参数与锚点；案例返回规范首页后继续选中原案例。实测发现并修复首页语言切换丢失project的问题，双语往返现在保留project、return及锚点。记录中的旧首页地址规范化是客户端history.replaceState，不是新增服务器301。

296页静态链接、锚点、双语对应、SEO检查通过。整页差异限定首页href、构建revision、导航资源缓存哈希；正文、CSS、图片、动效代码保持。5组导航回归套件通过。浏览器10项观察覆盖中英文切换、选中P36、双语案例往返、旧首页保留project和return、双语咨询入口。所有测试是本地QA，不是自然曝光、咨询或成交。

本地内容日期台账随真实导航变更更新294页为2026-10-22，不是纯构建刷新。官网内容和日期均未更改。只在项目源码、生成dist和本任务证据目录保存本地候选；未部署、未改服务器、未提交搜索平台或请求索引。

文件：source.diff、diff-check.json、static-checks.json、localization-checks.json、seo-checks.json、browser-check.json和receipt.json。before/保存修改前相关源码与HTML；baseline-dist-hashes.json可核验视觉资源未变。

本地预览：http://127.0.0.1:4178/?project=p36#work
英文预览：http://127.0.0.1:4178/en/?project=p36#work

未做手机真机验收。本轮没有生产发布或任何搜索平台提交。
