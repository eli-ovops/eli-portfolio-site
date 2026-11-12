# WorkBuddy 入门页本地修改

日期：2026-10-19。用户批准只做本地，不发布。

## 已落实

- 中英文入门页标题明确“腾讯 WorkBuddy / Tencent WorkBuddy”。
- 开头说明官方入口 workbuddy.cn，并保留先用练习材料、核对产物、再考虑正式账号的引导，以及功能和额度以当前官方资料为准的原有边界。
- 中英文搜索摘要同步产品身份及入门内容；Article、Open Graph 等元信息由原生成器同步，不另造版本。
- URL、分类、模板、CSS、JS、视觉和动效保持原样。保留原列表摘要，避免自动截句把卡片变成只有归属说明。
- 另外九篇 WorkBuddy 内容源逐项对比未变。

## 验证

- 构建通过，296 HTML；SEO 检查通过，204 个双语文章详情与294个规范地图地址。
- 排除缓存版本参数后，只有4个HTML发生内容变化：中英入门页、中英文章目录（该文章卡片标题及搜索文本）。其余292页一致。
- 78个受保护输出资产哈希未变。
- 内容日期台账只更新实际变化的4页为2026-10-19；普通重建不修改日期。原写作日期2026-10-17未伪装为今天。
- 浏览器模拟390px和360px检查中文、英文，未发现横向溢出；实际双向切换保留同一文章路径。
- 实际点击中文“免费聊聊”及英文“Let’s talk”，分别到达对应语言关于页#contact，联系区进入视口；未拨打电话、发送信息或提交表单。
- 临时视口覆盖已恢复，中文本地预览保留在侧边栏。手机检查为浏览器模拟，未冒充真机。

本地 revision：e2be96987b2798068e82。

预览：http://127.0.0.1:4178/articles/what-is-workbuddy.html?pv=e2be96987b2798068e82

英文：http://127.0.0.1:4178/en/articles/what-is-workbuddy.html?pv=e2be96987b2798068e82

修改源：content/tutorials/workbuddy.json、content/article-search-descriptions.json；另按实际内容变化维护content/page-updates.json及本地dist。

发布0、搜索平台提交0、邮件0。本地预览不证明收录、排名、点击或模型引用增长。

证据：seo-check.json、scope-check.json、browser-checks.json、rebuild-check.json、zh-mobile.png、en-mobile.png；修改前源文件和HTML保存在before中。
